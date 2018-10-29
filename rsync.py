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

def copy(src,des):
    fileInfo = os.stat(src)
    linkto = os.readlink(src)
    if os.path.islink(src):
        if os.path.exists(des):
            if os.path.isdir(des):
                os.symlink(linkto,des+ '/' +src)
            elif os.path.isfile(des):
                os.unlink(des)
                os.symlink(linkto,des)
        else:
            if des[-1] == '/':
                name = des.split('/')
                os.mkdir(os.path.abspath(name[0]))
                os.symlink(linkto,des+'/'+src)
            else:
                os.symlink(linkto,des)
    elif fileInfo.st_nlink>1:
        if os.path.exists(des):
            if os.path.isdir(des):
                os.link(linkto,des+ '/' +src)
            elif os.path.isfile(des):
                os.unlink(des)
                os.link(linkto,des)
        else:
            if des[-1] == '/':
                name = des.split('/')
                os.mkdir(os.path.abspath(name[0]))
                os.link(linkto,des+'/'+src)
            else:
                os.link(linkto,des)
    else:
        file1 = os.open(src,os.O_RDONLY)
        fileInfo = os.stat(src)
        linkto = os.readlink(src)
        if os.path.exists(des):
            if os.path.isdir(des):
                file2 = os.open(des+'/'+src,os.O_WRONLY|os.O_CREAT)
            elif os.path.isfile(des):
                file2 = os.open(des,os.O_WRONLY|os.O_CREAT)
        else:
            if des[-1] == '/':
                name = des.split('/')
                os.mkdir(os.path.abspath(name[0]))
                file2 = os.open(des+'/'+src,os.O_WRONLY|os.O_CREAT)
            else:
                file2 = os.open(des,os.O_WRONLY|os.O_CREAT)
    os.write(file2,os.read(file1,fileInfo.st_size))
    os.utime(file2,(fileInfo.st_ctime, fileInfo.st_mtime))
    os.chmod(file2,fileInfo.st_mode)
copy(args.SRC_FILE,args.DESTINATION)
