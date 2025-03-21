import os
#gets relative filepath of each file in the directory into a list
#what needs to be done is renaming these files with a defined format
#need fields for Device, Model, and Runtime
search_dir = os.getcwd()+"/toSort/"
os.chdir(search_dir)
files = filter(os.path.isfile, os.listdir(search_dir))
files = [os.path.join(search_dir, f) for f in files] # add path to each file
files.sort(key=lambda x: os.path.getmtime(x))

print(files)