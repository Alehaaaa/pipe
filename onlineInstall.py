from maya import cmds
from maya import mel
import urllib2
import shutil
import zipfile
import os



def formatPath(path):
    path = path.replace("/", os.sep)
    path = path.replace("\\", os.sep)
    return path

def download(downloadUrl, saveFile):
        
    try:    response        = urllib2.urlopen(downloadUrl, timeout=60)          
    except: pass
    
    if response is None: 
        cmds.warning("Error trying to install.")
        return
    
    
    fileSize        = int(response.info().getheaders("Content-Length")[0])
    fileSizeDl      = 0
    blockSize       = 128
    output          = open(saveFile,'wb')    
    progBar         = mel.eval('$tmp = $gMainProgressBar')
    
    
    cmds.progressBar( progBar,
                        edit=True,
                        beginProgress=True,
                        status='Downloading Pipeline...',
                        progress=0,
                        maxValue=100 )    
    
    while True:
        buffer = response.read(blockSize)
        if not buffer:
            output.close()
            cmds.progressBar(progBar, edit=True, progress=100)  
            cmds.progressBar(progBar, edit=True, endProgress=True)          
            break
    
        fileSizeDl += len(buffer)
        output.write(buffer)
        p = float(fileSizeDl) / fileSize *100
        
        cmds.progressBar(progBar, edit=True, progress=p)  
        
    return output


def PipelineInstall():

    mayaAppDir      = mel.eval('getenv MAYA_APP_DIR')    
    PipelinePath    = mayaAppDir + os.sep + cmds.about(v=True) + os.sep + "scripts"
    PipelineFolder  = PipelinePath + os.sep + "pipeline" + os.sep
    tmpZipFile      = "%s%stmp.zip"%(PipelinePath, os.sep)
    latest = urllib2.urlopen("https://github.com/Alehaaaa/pipe/releases/latest").url.split('/')[-1]
    DOWNLOAD_URL    = "https://github.com/Alehaaaa/pipe/archive/refs/tags/"+latest+".zip"
        
    #delete temp
    if os.path.isfile(tmpZipFile):     os.remove(tmpZipFile)   
    if os.path.isdir(PipelineFolder): shutil.rmtree(PipelineFolder)      
    
    output = download(DOWNLOAD_URL, tmpZipFile)    
    
    #uncompress file
    zfobj = zipfile.ZipFile(tmpZipFile)
    for name in zfobj.namelist():
        uncompressed = zfobj.read(name)
        
        # save uncompressed data to disk
        filename  = formatPath("%s%s%s"%(PipelinePath, os.sep, name))        
        d         = os.path.dirname(filename)
        
        if not os.path.exists(d): os.makedirs(d)
        if filename.endswith(os.sep): continue
        
        output = open(filename,'wb')
        output.write(uncompressed)
        output.close()
        
    #delete temp
    zfobj.close()
    pipe = formatPath("%s%s%s"%(PipelinePath, os.sep, 'pipe-latest'))
    if os.path.exists(pipe): os.rename(pipe, pipe.replace('pipe-latest','pipeline'))
    if os.path.isfile(tmpZipFile):     os.remove(tmpZipFile)
    
    import pipeline
    pipeline.start()
       
PipelineInstall()
