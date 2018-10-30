#!/usr/bin/env python3
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument("SRC_FILE", type=str)
parser.add_argument("DESTINATION", type=str)
parser.add_argument("-c", "--checksum", action ='store_true',
                   help='skip based on checksum, not mod-time & size')
parser.add_argument("-u", "--update", action ='store_true',
                   help='update destination files in-place')
args = parser.parse_args()


def getPath(des, fileName):
    if os.path.isdir(des):
        if des[-1] != '/':
            return des +'/'+fileName
        else:
            return des+fileName
    return des


#create a folder if des has '/'' at bottom
def createFolder(des):
    name = des.split('/')
    os.mkdir(os.path.abspath(name[0]))


def setTimeAndMode(des,fInfo,type):
    if type == 1:
        os.utime(des,(fInfo.st_atime, fInfo.st_mtime),follow_symlinks = False)
    else:
        os.utime(des,(fInfo.st_atime, fInfo.st_mtime))
        os.chmod(des,fInfo.st_mode)

def copySym(src,des,linkto):
    fileInfo = os.lstat(src)
    if des[-1] == '/':
        createFolder(des)
    os.symlink(linkto,getPath(des,src))
    setTimeAndMode(getPath(des,src),fileInfo,1)


def copyHard(src,des):
    fileInfo = os.stat(src)
    if des[-1] == '/':
        createFolder(des)
    os.link(src,getPath(des,src))
    setTimeAndMode(getPath(des,src),fileInfo,1)


def copyNor(src,des):
    file1 = os.open(src,os.O_RDONLY)
    fileInfo1 = os.stat(src)
    contFile1 = os.read(file1,fileInfo1.st_size)
    if os.path.exists(des):
        file2 = os.open(getPath(des,src),os.O_WRONLY|os.O_CREAT)
        fileInfo2 = os.stat(des)
        contFile2 = os.read(file2,fileInfo2.st_size)
        count = 0
        # while count < fileInfo1.st_size:

    else:
        if des[-1] == '/':
            createFolder(des)
            file2 = os.open(getPath(des,src),os.O_WRONLY|os.O_CREAT)
            os.write(file2,contFile1)
    setTimeAndMode(file2,fileInfo,0)

def main():
    if os.path.islink(args.SRC_FILE):
        linkto = os.readlink(args.SRC_FILE)
        copySym(args.SRC_FILE,args.DESTINATION,linkto)
    elif os.stat(args.SRC_FILE).st_nlink>1:
        copyHard(args.SRC_FILE,args.DESTINATION)

if __name__ == '__main__':
    main()
