#!/usr/bin/env python3
import argparse
import os


def getPathDes(des, fileName):
    if os.path.isdir(des):
        if des[-1] != '/':
            return des + '/' + fileName
        else:
            return des + fileName
    return des


def getPathName(src):
    if '/' in src:
        return os.path.basename(src)
    return src


def getInfo(item):
    if not os.path.exists(item):
        return False
    elif os.path.islink(item):
        return os.lstat(item)
    return os.stat(item)


def createDir(src, des, isSRCMore, r_option):
    if isSRCMore and not os.path.exists(des):
        os.mkdir(des)
    elif r_option and not os.path.exists(des):
        os.mkdir(des)
    elif not os.path.exists(des) and '/' in des:
        if des[-1] == '/':
            os.mkdir(des)
        else:
            if not os.path.exists(os.path.dirname(des)):
                os.mkdir(os.path.dirname(des))


def checkSymlink(item):
    return os.path.islink(item)


def checkHardlink(item):
    return os.stat(item).st_nlink > 1


def checkMTime(src, des):
    if getInfo(des):
        return getInfo(src).st_mtime == getInfo(des).st_mtime
    return False


def checkSize(src, des):
    if getInfo(des):
        return getInfo(src).st_size == getInfo(des).st_size
    return False


def updateTime_Per(des, srcInfo, isSymLink):
    if isSymLink:
        os.utime(des, (srcInfo.st_atime, srcInfo.st_mtime),
                 follow_symlinks=False)
    else:
        os.utime(des, (srcInfo.st_atime, srcInfo.st_mtime))
        os.chmod(des, srcInfo.st_mode)


def updateContent(src, des):
    f1 = os.open(src, os.O_RDONLY)
    f2 = os.open(des, os.O_RDWR | os.O_CREAT)
    f1Content = os.read(f1, os.path.getsize(src))
    f2Content = os.read(f2, os.path.getsize(des))
    length = 0
    while length < os.path.getsize(src):
        os.lseek(f1, length, 0)
        os.lseek(f2, length, 0)
        if length < len(f2Content):
            if f2Content[length] != f1Content[length]:
                os.write(f2, os.read(f1, 1))
        else:
            os.write(f2, os.read(f1, 1))
        length += 1


def copyFileLink(src, des):
    if os.path.exists(des):
        os.unlink(des)
    if checkSymlink(src):
        pathSRC = os.readlink(src)
        os.symlink(pathSRC, des)
    elif checkHardlink(src):
        os.link(src, des)


def copyFileNor(src, des):
    f1 = os.open(src, os.O_RDONLY)
    if os.path.exists(des):
        if getInfo(src).st_size >= getInfo(des).st_size:
            if checkPerFileFault(des):
                os.unlink(des)
            updateContent(src, des)
        else:
            os.remove(des)
            f2 = os.open(des, os.O_WRONLY | os.O_CREAT)
            os.write(f2, os.read(f1, os.path.getsize(f1)))
    else:
        f2 = os.open(des, os.O_WRONLY | os.O_CREAT)
        os.write(f2, os.read(f1, os.path.getsize(f1)))


def copyFile(src, des):
    if checkSymlink(src) or checkHardlink(src):
        copyFileLink(src, des)
    else:
        copyFileNor(src, des)


def checkNoFileFault(item):
    if not getInfo(item):
        print("rsync: link_stat \"" + os.path.abspath(item) +
              "\" failed: No such file or directory (2)")
        return True
    return False


def checkPerFileFault(item):
    try:
        f1 = os.open(item, os.O_RDONLY & os.O_WRONLY)
    except PermissionError:
        return True
    return False


def copy(src, des, u_option, c_option, r_option, isSRCMore, checkRALL):
    if checkNoFileFault(src):
        return
    if checkPerFileFault(src):
        print("rsync: send_files failed to open \""+os.path.abspath(src) +
              "\": Permission denied (13)")
        return
    createDir(src, des, isSRCMore, r_option)
    des1 = getPathDes(des, getPathName(src))
    srcInfo = getInfo(src)
    if u_option:
        if srcInfo.st_mtime > getInfo(des1).st_mtime:
            copyFile(src, des1)
    elif c_option:
        copyFile(src, des1)
    elif r_option:
        if not checkRALL:
            things = src.split('/')
            des1 = des
            for i in range(len(things)-1):
                des1 += '/' + things[i]
                createDir(src, des1, isSRCMore, r_option)
            des1 += '/' + things[-1]
            copyFile(src, des1)
        else:
            things = src.split('/')
            things.pop(0)
            des1 = des
            for i in range(len(things)-1):
                des1 += '/' + things[i]
                createDir(src, des1, isSRCMore, r_option)
            des1 += '/' + things[-1]
            copyFile(src, des1)

    else:
        if not checkMTime(src, des1) or not checkSize(src, des1):
            copyFile(src, des1)
    updateTime_Per(des1, srcInfo, checkSymlink(src))


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles


def rsync(srcs, des, u_option, c_option, r_option):
    if r_option:
        for src in srcs:
            if os.path.isdir(src):
                for it in getListOfFiles(src):
                    if src[-1] != '/':
                        copy(it, des, u_option, c_option,
                             r_option, len(srcs) > 1, False)
                    else:
                        copy(it, des, u_option, c_option,
                             r_option, len(srcs) > 1, True)
            if os.path.isfile(src):
                copy(src, des, u_option, c_option,
                     r_option, len(srcs) > 1, False)
    else:
        for src in srcs:
            copy(src, des, u_option, c_option, r_option, len(srcs) > 1, False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("SRC_FILE", type=str, nargs="+")
    parser.add_argument("DESTINATION", type=str)
    parser.add_argument("-c", "--checksum", action='store_true',
                        help='skip based on checksum, not mod-time & size')
    parser.add_argument("-u", "--update", action='store_true',
                        help='update destination files in-place')
    parser.add_argument("-r", "--recursive", action='store_true',
                        help='recurse into directories')
    args = parser.parse_args()
    rsync(args.SRC_FILE, args.DESTINATION, args.update,
          args.checksum, args.recursive)


if __name__ == '__main__':
    main()
