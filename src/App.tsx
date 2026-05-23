 
import {useEffect,  useState, useRef} from 'react';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import CircularProgress from '@mui/material/CircularProgress';
 
import type { GridColDef } from '@mui/x-data-grid';
import {DataGrid} from '@mui/x-data-grid/DataGrid';
import Paper from '@mui/material/Paper';
import SettingsIcon from '@mui/icons-material/Settings';
import supportButton from "./assets/images/buy_me_a_coffee.png";
import logo from "./assets/images/youtube_downloader.png";
import Divider from '@mui/material/Divider';

import './global.module.css'

const columns: Array<GridColDef> = [
  { field: 'id', headerName: 'ID', width: 70, align: 'center'},
  { field: 'title', headerName: 'Title', width: 310 },
  { field: 'type', headerName: 'File Type', width: 75, align: 'center' },
  { field: 'format', headerName: 'Format', width: 65, align: 'center' },
  {
    field: 'status',
    headerName: 'Status',
    width: 150,
    valueGetter: (value, row) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      if(row.status === "Downloading"){
        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-argument
        return `${Math.round(row.percentage)}%`
      }
      
      return value;
    },
  },
];

const paginationModel = { page: 0, pageSize: 5 };

interface RowItem {
  id: number;
  url: string;
  title: string;
  type: string;
  format: string;
  status: string;
  percentage?: number;
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any, prefer-const
let queues: Array<any> = [];

function App() {
  const downloadPath = localStorage.getItem("download_directory");
  const [url, setUrl] = useState('');
  const [openSettings, setOpenSettings] = useState(false);
  const [rows, setRows] = useState<Array<RowItem>>([]);
  const [type, setType] = useState<FileType>('audio');
  const [format, setFormat] = useState('mp3');
  const [formatItems, setFormatItems] = useState<Array<string>>([]);
  const [downloadDirectory, setDownloadDirectory] = useState(downloadPath);
  const [isDownloading, setIsDownloading] = useState(false);
  const [ffmpegPath, setFfmpegPath] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");

  const folderPickerRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-misused-promises
    setTimeout(async () => {
      setLoadingMessage("Initializing ffmpeg...")
      setLoading(true);
      const handler = await YTDLP.initializeFfmpeg();
      handler.onFinished.connect((path) => {
        console.log(`ffmpeg path ${path}`)
        setFfmpegPath(path);
        setLoading(false);
      })

      if(!downloadPath){
        YTDLP.getDefaultDownloadDirectory().then((directory) => {
          setDownloadDirectory(directory);
        });
      }
    }, 600);
    
    if (folderPickerRef.current) {
      folderPickerRef.current.setAttribute('directory', '');
      folderPickerRef.current.setAttribute('webkitdirectory', '');
    }
  }, []);
  
  useEffect(() => {
    if(type==='video'){
       
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFormatItems(['mp4', 'webm']);
      setFormat('mp4');
    } else {
      setFormatItems(['mp3', 'aac', 'm4a']);
      setFormat('mp3');
    }
  }, [type])

  const handleAddToQueue = async () => {
    const title = await YTDLP.getTitle(url);
    setRows(previous => {
       
      return [
         
        ...previous,
        {
          id: rows.length + 1,
          url,
          title,
          type,
          format,
          status: 'Queued'
        }
      ]
    });
    setUrl('');
  }

  const handleClearQueue = () => {
    setRows([]);
  }

  const handleUpdateProgress = (jsonString: string) => {
    const progress = JSON.parse(jsonString) as RowItem;
    
    if(progress.status === "Finished") {
      setRows(previous => previous.filter(row => row.id !== progress.id));
    } else {
      setRows(previous => previous.map(row => {
        if(row.id === progress.id){
          return progress;
        }
        
        return row;
      }));
    }
    
  }
  const handleDownload = async () => {
    setIsDownloading(true);
    for(const row of rows){
      // eslint-disable-next-line no-await-in-loop
      const queue = await YTDLP.download(JSON.stringify({...row, noPlaylist: true, downloadDirectory}), JSON.stringify({"ffmpeg_location": ffmpegPath}))
       
      queue.onProgress.connect(handleUpdateProgress);
      queues.push(queue.start());
    }
    Promise.all(queues).then(() => {
      setIsDownloading(false);
    });
  }

  const handleSettingsClose = () => {
    setOpenSettings(false);
  }


  return (
    <div className="flex flex-col item-center justify-center p-5">
      <div className="fixed right-0 top-0 mr-5 mt-5">
        <SettingsIcon onClick={() => { setOpenSettings(true); }}/>
      </div>
      <div className='logo-container flex justify-center'>
        <img alt="Youtube Downloader" className='logo w-50' src={logo} />
      </div>
      <h1 className="text-center text-2xl font-bold mt-10 mb-5">Youtube Downloader</h1>
      <FormControl fullWidth style={{marginBottom: 20}}>
        <TextField id="outlined-basic" label="Url" value={url} variant="outlined" onChange={(event) => { setUrl(event.target.value); } } />
      </FormControl>
      <FormControl fullWidth style={{marginBottom: 20}}>
        <InputLabel id="type-select-label">Type</InputLabel>
        <Select
          id="type-select"
          label="Type"
          labelId="type-select-label"
          value={type}
          onChange={(value) => {setType(value.target.value);}}
        >
          <MenuItem value="video">Video</MenuItem>
          <MenuItem value="audio">Audio</MenuItem>
        </Select>
      </FormControl>
      <FormControl fullWidth style={{marginBottom: 20}}>
        <InputLabel id="file-type-label">File Type</InputLabel>
        <Select
          id="file-type-label-select"
          label="File Type"
          labelId="file-type-label"
          value={format}
          
          onChange={(value) => {setFormat(value.target.value);}}
        >
          {
            formatItems.map((item, index) => {
              return <MenuItem key={index} value={item}>{item}</MenuItem>
            })
          }
          
        </Select>
      </FormControl>
      <div className="flex flex-row">
        <Button disabled={isDownloading} variant="contained" onClick={handleAddToQueue}>
          Add to Queue
        </Button>
        <Button disabled={rows.length === 0} style={{marginLeft:10}} variant="contained" onClick={handleDownload}>
          Download
        </Button>
        <Button disabled={rows.length === 0 || isDownloading} style={{marginLeft:10}} variant="contained" onClick={handleClearQueue}>
          Clear Queue
        </Button>
        <a href="https://www.buymeacoffee.com/ekoputraprm" style={{marginLeft:10}} target="_blank">
          <img alt="Buy Me A Coffee" src={supportButton} style={{height: "41px !important", width: "174px !important", boxShadow: "0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important",WebkitBoxShadow: "0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important"}} />
        </a>
      </div>
      <Paper sx={{ height: 400, width: '100%' }}>
        <DataGrid
          columns={columns}
          initialState={{ pagination: { paginationModel } }}
          pageSizeOptions={[5, 10]}
          rows={rows}
          sx={{ border: 0 }}
        />
      </Paper>
      <Dialog open={loading}>
        <DialogContent>
          <div className='flex flex-col justify-center items-center'>
            <CircularProgress enableTrackSlot size={40} />
            <span className='mt-5'>{loadingMessage}</span>
          </div>
        </DialogContent>
      </Dialog>
      <Dialog fullWidth open={openSettings} onClose={handleSettingsClose}>
        <DialogTitle>Settings</DialogTitle>
        <Divider />
        <DialogContent>
          <div className='flex flex-col container'>
            <FormControl fullWidth style={{marginBottom: 20}}>
              <FormLabel style={{marginBottom:10}}>Download directory</FormLabel>
              <input ref={folderPickerRef} className="hidden" id="folder-picker" type="file"  />
              <div className='flex flex-row items-center'>
                <label className='grow border-b-neutral-500 border-2' style={{padding: "10px 20px"}}>{downloadDirectory}</label>
                <button 
                  className='shrink' 
                  style={{padding: "10px 10px", backgroundColor: "rgb(25, 118, 210)", color: "white", border: "none", cursor: "pointer"}}
                  // eslint-disable-next-line unicorn/prevent-abbreviations
                  onClick={(e) => {
                     
                    YTDLP.selectDirectory().then((directory) => {
                      if(directory){
                        setDownloadDirectory(directory);
                        localStorage.setItem("download_path", directory);
                      }
                    });
                    e.stopPropagation();
                  }}>Select Folder</button>
              </div>
              
            </FormControl>
          </div>
        </DialogContent>
        
      </Dialog>
    </div>
  )
}

export default App
