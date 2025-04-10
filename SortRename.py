import os
#gets relative filepath of each file in the directory into a list
#what needs to be done is renaming these files with a defined format
#need fields for Device, Model, and Runtime
device="D47"#set up variables
model="M10"
runtime="tf"
label=device+"-"+model+"-"+runtime+"-"

os.makedirs(os.getcwd()+"/completed"+"/"+label+"/")#make output directory

search_dir = os.getcwd()+"/toSort/"#get search directory
out_dir = os.getcwd()+"/completed"+"/"+label+"/"#get output directory
os.chdir(search_dir)#changes directory to search directory
files = filter(os.path.isfile, os.listdir(search_dir))
files = [os.path.join(search_dir, f) for f in files] # add path to each file
files.sort(key=lambda x: os.path.getmtime(x))

trace=1

for file in files:
    if trace < 10:
        os.rename(file, out_dir + label + "0" + str(trace)+".h5")
    else:
        os.rename(file, out_dir + label + str(trace)+".h5")
    trace+=1

print(files)