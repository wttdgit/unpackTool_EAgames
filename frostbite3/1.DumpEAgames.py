import dbo
import noncas
import ebx
import payload
import cas
import das
import os
from struct import pack,unpack
import res
gameDirectory = os.path.normpath(input(r"input_game_path_like: Z:\SteamLibrary\steamapps\common\Battlefield 4："))
targetDirectory = os.path.normpath(input(r"input_dump_path_like: E:\_unpack_Battlefield4："))
def dump(tocPath,baseTocPath,outPath):
    """Take the filename of a toc and dump all files to the targetFolder."""
    toc=dbo.readToc(tocPath)
    if not (toc.get("bundles") or toc.get("chunks")): return
    sbPath=tocPath[:-3]+"sb"
    sb=open(sbPath,"rb")
    chunkPathToc=os.path.join(outPath,"chunks")
    bundlePath=os.path.join(outPath,"bundles")
    ebxPath=os.path.join(bundlePath,"ebx")
    resPath=os.path.join(bundlePath,"res")
    chunkPath=os.path.join(bundlePath,"chunks")
    if toc.get("cas"):
        for tocEntry in toc.get("bundles"):
            if tocEntry.get("base"): continue
            sb.seek(tocEntry.get("offset"))
            bundle=dbo.DbObject(sb)
            if tocEntry.get("delta"):
                writePayload=payload.casPatchedBundlePayload
            else:
                writePayload=payload.casBundlePayload
            for entry in bundle.get("ebx",list()):
                path=os.path.join(ebxPath,entry.get("name")+".ebx")
                if writePayload(entry,path,False):
                    ebx.addEbxGuid(path,ebxPath)
            for entry in bundle.get("res",list()):
                res.addToResTable(entry.get("resRid"),entry.get("name"),entry.get("resType"),entry.get("resMeta"))
                path=os.path.join(resPath,entry.get("name")+res.getResExt(entry.get("resType")))
                writePayload(entry,path,False)
            for entry in bundle.get("chunks",list()):
                path=os.path.join(chunkPath,entry.get("id").format()+".chunk")
                writePayload(entry,path,True)
        for entry in toc.get("chunks"):
            targetPath=os.path.join(chunkPathToc,entry.get("id").format()+".chunk")
            payload.casChunkPayload(entry,targetPath)
    else:
        for tocEntry in toc.get("bundles"):
            if tocEntry.get("base"): continue
            sb.seek(tocEntry.get("offset"))
            if tocEntry.get("delta"):
                baseToc=dbo.readToc(baseTocPath)
                for baseTocEntry in baseToc.get("bundles"):
                    if baseTocEntry.get("id").lower() == tocEntry.get("id").lower():
                        break
                else:
                    pass
                basePath=baseTocPath[:-3]+"sb"
                base=open(basePath,"rb")
                base.seek(baseTocEntry.get("offset"))
                bundle=noncas.patchedBundle(base, sb)
                base.close()
                writePayload=payload.noncasPatchedBundlePayload
                sourcePath=[basePath,sbPath]
            else:
                bundle=noncas.unpatchedBundle(sb)
                writePayload=payload.noncasBundlePayload
                sourcePath=sbPath
            for entry in bundle.ebx:
                path=os.path.join(ebxPath,entry.name+".ebx")
                if writePayload(entry,path,sourcePath):
                    ebx.addEbxGuid(path,ebxPath)
            for entry in bundle.res:
                res.addToResTable(entry.resRid,entry.name,entry.resType,entry.resMeta)
                path=os.path.join(resPath,entry.name+res.getResExt(entry.resType))
                writePayload(entry,path,sourcePath)
            for entry in bundle.chunks:
                path=os.path.join(chunkPath,entry.id.format()+".chunk")
                writePayload(entry,path,sourcePath)
        for entry in toc.get("chunks"):
            targetPath=os.path.join(chunkPathToc,entry.get("id").format()+".chunk")
            payload.noncasChunkPayload(entry,targetPath,sbPath)
    sb.close()
def dumpRoot(dataDir,patchDir,outPath):
    os.makedirs(outPath,exist_ok=True)
    for dir0, dirs, ff in os.walk(dataDir):
        for fname in ff:
            if fname[-4:]==".toc":
                fname=os.path.join(dir0,fname)
                localPath=os.path.relpath(fname,dataDir)
                print(localPath)
                patchedName=os.path.join(patchDir,localPath)
                if os.path.isfile(patchedName):
                    dump(patchedName,fname,outPath)
                dump(fname,None,outPath)
def findCats(dataDir,patchDir,readCat):
    for dir0, dirs, ff in os.walk(dataDir):
        for fname in ff:
            if fname=="cas.cat":
                fname=os.path.join(dir0,fname)
                localPath=os.path.relpath(fname,dataDir)
                print("Reading %s..." % localPath)
                readCat(fname)
                patchedName=os.path.join(patchDir,localPath)
                if os.path.isfile(patchedName):
                    print("Reading patched %s..." % os.path.relpath(patchedName,patchDir))
                    readCat(patchedName)
gameDirectory=os.path.normpath(gameDirectory)
targetDirectory=os.path.normpath(targetDirectory)
payload.zstdInit()
print("Loading RES names...")
res.loadResNames()
tocLayout=dbo.readToc(os.path.join(gameDirectory,"Data","layout.toc"))
if not tocLayout.getSubObject("installManifest") or \
    not tocLayout.getSubObject("installManifest").getSubObject("installChunks"):
    if not os.path.isfile(os.path.join(gameDirectory,"Data","das.dal")):
        dataDir=os.path.join(gameDirectory,"Data")
        updateDir=os.path.join(gameDirectory,"Update")
        patchDir=os.path.join(updateDir,"Patch","Data")
        if not tocLayout.getSubObject("installManifest"):
            readCat=cas.readCat1
        else:
            readCat=cas.readCat2
        catPath=os.path.join(dataDir,"cas.cat")
        if os.path.isfile(catPath):
            print("Reading cat entries...")
            readCat(catPath)
            patchedCat=os.path.join(patchDir,os.path.relpath(catPath,dataDir))
            if os.path.isfile(patchedCat):
                print("Reading patched cat entries...")
                readCat(patchedCat)
        if os.path.isdir(updateDir):
            for dir in os.listdir(updateDir):
                if dir=="Patch":
                    continue
                print("Extracting DLC %s..." % dir)
                dumpRoot(os.path.join(updateDir,dir,"Data"),patchDir,targetDirectory)
        print("Extracting main game...")
        dumpRoot(dataDir,patchDir,targetDirectory)
    else:
        dataDir=os.path.join(gameDirectory,"Data")
        print("Reading dal entries...")
        dalPath=os.path.join(dataDir,"das.dal")
        das.readDal(dalPath)
        print("Extracting main game...")
        das.dumpRoot(dataDir,targetDirectory)
        print("Extracting FE...")
        das.dumpFE(dataDir,targetDirectory)
else:
    dataDir=os.path.join(gameDirectory,"Data")
    updateDir=os.path.join(gameDirectory,"Update")
    patchDir=os.path.join(gameDirectory,"Patch")
    if tocLayout.getSubObject("installManifest").get("maxTotalSize")!=None:
        readCat=cas.readCat3
    else:
        readCat=cas.readCat4
    if os.path.isdir(updateDir):
        for dir in os.listdir(updateDir):
            print("Extracting DLC %s..." % dir)
            dir=os.path.join(updateDir,dir,"Data")
            findCats(dir,patchDir,readCat)
            dumpRoot(dir,patchDir,targetDirectory)
    print("Extracting main game...")
    findCats(dataDir,patchDir,readCat)
    dumpRoot(dataDir,patchDir,targetDirectory)
if not os.path.isdir(targetDirectory):
    print("Nothing was extracted, did you set input path correctly?")
    sys.exit(1)
print("Writing EBX GUID table...")
ebx.writeGuidTable(targetDirectory)
print ("Writing RES table...")
res.writeResTable(targetDirectory)
payload.zstdCleanup()