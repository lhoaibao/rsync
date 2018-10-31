#!/usr/bin/env python3
import argparse
import os


def getPath(des, fileName):
    if os.path.isdir(des):
        if des[-1] != '/':
            return des + '/' + fileName
        else:
            return des + fileName
    return des


# create a folder if des has '/'' at bottom
def createFolder(des):
    name = des.split('/')
    os.mkdir(os.path.abspath(name[0]), 0o755)


def setTimeAndMode(des, fInfo, type):
    if type == 1:
        os.utime(des, (fInfo.st_atime, fInfo.st_mtime), follow_symlinks=False)
    else:
        os.utime(des, (fInfo.st_atime, fInfo.st_mtime))
        os.chmod(des, fInfo.st_mode)


def copySym(src, des, linkto):
    fileInfo = os.lstat(src)
    if des[-1] == '/':
        createFolder(des)
    os.symlink(linkto, getPath(des, src))
    setTimeAndMode(getPath(des, src), fileInfo, 1)


def copyHard(src, des):
    fileInfo = os.stat(src)
    if des[-1] == '/':
        createFolder(des)
    os.link(src, getPath(des, src))
    setTimeAndMode(getPath(des, src), fileInfo, 1)


def copyNor(src, des):
    file1 = os.open(src, os.O_RDWR)
    fileInfo1 = os.stat(src)
    contFile1 = os.read(file1, fileInfo1.st_size)
    if os.path.exists(des):
        if os.path.isfile(des):
            fileInfo2 = os.stat(des)
            if fileInfo1.st_size >= fileInfo2.st_size:
                file2 = os.open(getPath(des, src), os.O_RDWR | os.O_CREAT)
                contFile2 = os.read(file2, fileInfo2.st_size)
                count = 0
                while count < fileInfo1.st_size:
                    os.lseek(file1, count, 0)
                    os.lseek(file2, count, 0)
                    if count < len(contFile2):
                        if contFile2[count] != contFile1[count]:
                            os.write(file2, os.read(file1, 1))
                    else:
                        os.write(file2, os.read(file1, 1))
                    count = count + 1
                setTimeAndMode(file2, fileInfo1, 0)
        else:
            file2 = os.open(getPath(des, src), os.O_WRONLY | os.O_CREAT)
            os.write(file2, contFile1)
            setTimeAndMode(file2, fileInfo1, 0)

    else:
        if des[-1] == '/':
            createFolder(des)
        file2 = os.open(getPath(des, src), os.O_WRONLY | os.O_CREAT)
        os.write(file2, contFile1)
        setTimeAndMode(file2, fileInfo1, 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("SRC_FILE", type=str)
    parser.add_argument("DESTINATION", type=str)
    parser.add_argument("-c", "--checksum", action='store_true',
                        help='skip based on checksum, not mod-time & size')
    parser.add_argument("-u", "--update", action='store_true',
                        help='update destination files in-place')
    args = parser.parse_args()
    if not os.path.exists(args.SRC_FILE):
        print("rsync: link_stat \"" + os.path.abspath(args.SRC_FILE) +
              "\" failed: No such file or directory (2)")
        return
    try:
        f1 = os.open(args.SRC_FILE, os.O_RDONLY)
    except PermissionError:
        print("rsync: send_files failed to open \"" +
              os.path.abspath(args.SRC_FILE)+"\": Permission denied (13)")
        return
    ifo1 = os.stat(args.SRC_FILE)
    ifo2 = os.stat(args.DESTINATION)
    if not args.update:
        if (ifo1.st_size != ifo2.st_size)or(ifo1.st_mtime != ifo2.st_mtime):
            if os.path.islink(args.SRC_FILE):
                linkto = os.readlink(args.SRC_FILE)
                copySym(args.SRC_FILE, args.DESTINATION, linkto)
            elif os.stat(args.SRC_FILE).st_nlink > 1:
                copyHard(args.SRC_FILE, args.DESTINATION)
            else:
                copyNor(args.SRC_FILE, args.DESTINATION)
    else:
        if ifo1.st_mtime > ifo2.st_mtime:
            if os.path.islink(args.SRC_FILE):
                linkto = os.readlink(args.SRC_FILE)
                copySym(args.SRC_FILE, args.DESTINATION, linkto)
            elif os.stat(args.SRC_FILE).st_nlink > 1:
                copyHard(args.SRC_FILE, args.DESTINATION)
            else:
                copyNor(args.SRC_FILE, args.DESTINATION)


if __name__ == '__main__':
    main()
