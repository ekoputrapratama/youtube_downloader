import os
import subprocess
import shutil
import getpass

manifest_template = """<?xml version="1.0" encoding="utf-8"?>
<Package
  xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
  xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
  xmlns:uap10="http://schemas.microsoft.com/appx/manifest/uap/windows10/10"
  xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
  IgnorableNamespaces="uap rescap">

  <Identity Name="Mixaline.YTDLPGui" Version="1.0.8.0" Publisher="CN=21A8CF7A-836D-4098-B460-D62ADAC65D12" ProcessorArchitecture="x64"  />
  <Properties>
    <DisplayName>YTDLP Gui</DisplayName>
    <PublisherDisplayName>Mixaline</PublisherDisplayName>
    <Logo>youtube_downloader.png</Logo>
  </Properties>

  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.22000.0" />
  </Dependencies>

  <Resources>
    <Resource Language="en-us"/>
  </Resources>
  <Applications>
    <Application Id="App" Executable="youtube_downloader.exe" EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements
        DisplayName="YTDLP Gui"
        Description="A portable, intuitive graphical user interface for yt-dlp, built with PySide6. This application allows you to easily fetch content from YouTube and other supported platforms without touching the command line."
        BackgroundColor="transparent"
        Square150x150Logo="youtube_downloader.png"
        Square44x44Logo="youtube_downloader.png">
        <uap:DefaultTile Wide310x150Logo="youtube_downloader.png"/>
      </uap:VisualElements>
    </Application>
  </Applications>

  <Capabilities>
    <rescap:Capability Name="runFullTrust"/>
  </Capabilities>
</Package>
"""

if __name__ == "__main__":
  packageDir = os.path.join(os.path.dirname(__file__), '../dist/package')
  certFilePath = os.path.join(os.path.dirname(__file__), '../certs/mixaline.pfx')
  os.makedirs(packageDir, 0x777, exist_ok=True)
  with open(os.path.join(packageDir, "AppxManifest.xml"), "w") as f:
    f.write(manifest_template)

  iconPath = os.path.join(os.path.dirname(__file__), '..', 'src', 'assets', 'images', 'youtube_downloader.png')
  exePath = os.path.join(os.path.dirname(__file__), '..', 'dist', 'youtube_downloader.exe')
  packagePath = os.path.join(os.path.dirname(__file__), '..', 'dist', 'Mixaline.YTDLPGui.msix')
  shutil.copy(iconPath, packageDir)
  shutil.copy(exePath, packageDir)
  subprocess.run(["makeappx.exe", "pack", "/d", packageDir, "/p", packagePath])
  passwd = getpass.getpass("Enter your password: ")
  subprocess.run(["signtool.exe", "sign", "/fd", "SHA256", "/a", "/f", certFilePath, "/p", passwd, packagePath])
  shutil.rmtree(packageDir)
