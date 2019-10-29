
import sys
import fileinfo as fi

if __name__ == "__main__":
    
    #__import__(sys.argv[1])
    cfile = fi.File(sys.argv[1])
    sys.path.append(cfile.get_dir())
    __import__(cfile.get_name().replace(".py",""))
