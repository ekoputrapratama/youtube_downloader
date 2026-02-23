 
import {useEffect,  useState} from 'react';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import type { GridColDef } from '@mui/x-data-grid';
// eslint-disable-next-line no-duplicate-imports
import { DataGrid } from '@mui/x-data-grid';
import Paper from '@mui/material/Paper';
import supportButton from "./assets/images/support_me_on_kofi_blue.webp";
import logo from "./assets/images/youtube_downloader.png";

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
  const [url, setUrl] = useState('');
  const [rows, setRows] = useState<Array<RowItem>>([]);
  const [type, setType] = useState<FileType>('audio');
  const [format, setFormat] = useState('mp3');
  const [formatItems, setFormatItems] = useState<Array<string>>([]);
  
  
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
  const handleUpdateProgress = (jsonString: string) => {
    const progress = JSON.parse(jsonString) as RowItem;
    
    console.log("handleUpdateProgress", progress)
    if(progress.status === "Finished") {
      console.log("queues", queues);
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
    console.log("handleDownload")
    // const downloads = [];
    
    for(const row of rows){
      // eslint-disable-next-line no-await-in-loop
      const queue = await YTDLP.download(JSON.stringify({...row, noPlaylist: true}))
       
      queue.onProgress.connect(handleUpdateProgress);
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      queue.start();
      queues.push(queue.start());
    }
    // const queue = await YTDLP.download(JSON.stringify({url, type, format, noPlaylist: true})).catch(console.error)
    console.log("queues", queues);
  }

  return (
    <div className="flex flex-col item-center justify-center p-5">
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
        <Button variant="contained" onClick={handleAddToQueue}>
          Add to Queue
        </Button>
        <Button disabled={rows.length === 0} style={{marginLeft:10}} variant="contained" onClick={handleDownload}>
          Download
        </Button>
        <Button disabled={rows.length === 0} style={{marginLeft:10}} variant="contained" onClick={() => { setRows([]); }}>
          Clear Queue
        </Button>
        <a href="https://ko-fi.com/ekoputrapratama" style={{maxWidth: 180}} target='_blank' onClick={() => YTDLP.openUrl("https://ko-fi.com/ekoputrapratama")}>
          <img alt="Support me" src={supportButton} />
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
    </div>
  )
}

export default App
