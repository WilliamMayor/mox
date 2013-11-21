# mox

mox scans directories for predetermined commands and executes them. 

For example, if you run mox on a directory that contains a file called `mox_commit` and that contains a message:

	$ cat mox_commit
	this is a commit message
	

Then mox will perform a `git commit` inside that directory using the provided message. 

## Why?

Think of it as very slow, very limited SSH. This can be useful when you want to interact with files on a server but don't have a device that handles SSH (or maybe the server doesn't handle SSH). The reason I built mox was to let me run git commands on files in a Dropbox directory that I alter using my iPad. The iPad doesn't support git or SSH very well but it has great support for Dropbox and plenty of apps let me develop code. with mox running on a VPS I can make changes to my code from my iPad, commit those changes and push them to GitHub. The VPS simply performs the tasks I give it via the mox command files.

## How?

mox is a simple python project that takes a directory,  scans it for command files and runs the python code associated with that command file. It is easily extensible and can run just about any command you give it. mox assumes that the system is using [incron](http://linux.die.net/man/5/incrontab) to run mox over directories that change. 

### Available Commands

Currently mox supports:

	mox_commit
		contents: commit message
		cmd: git commit -a -m "[contents]"
		
		Use the contents of the file as the commit message and commit the local changes. The files in the scanned directory (excluding mox_commit) are git added to the repo before the commit
	mox_push
		contents: none
		cmd: git push
		
		Push to the default remote
	mox_pull
		contents: none
		cmd: git pull
		
		Pull from the default remote
	mox_clone
		contents: git repo URL
		cmd: git clone [contents]
		
		Use the contents of the file as the URL for the remote repo and clone into the directory where mox_clone was found. Also sets up incron to monitor files changes and run mox over them
	mox_branch
		contents: branch name
		cmd: git branch [contents]
		
		Create a new branch with the name provided in the file  Immediately push the branch to the default remote. 
	mox_merge
		contents: merge arguments, separated by a new line
		cmd: git checkout [contents[1]]; git merge [contents[0]]
		
		Checkout argument 2 and merge into argument 1
	mox_checkout
		contents: the branch/commit to checkout
		cmd: git checkout [contents]
		
		Checks out the branch/commit provided in the file
	mox_delete
		contents: the name of the directory
		cmd: rm -rf .
		
		Deletes this directory and all associated files. Removes the directory from incron. The contents of the file have to match the directory name for this command to run. 

When mox detects a file with one of these names it runs the specified action. The `mox_*` file is deleted and if anything goes wrong a `mox_error` file is created in the directory above the scanned directory. 

## Installation

I'm assuming that you're installing mox onto a Linux (or at least Unix) based server. There's no reason that mox won't work on a desktop machine but I've not tried it. I'm doubtful that mox would run on Windows. 

First download the mox source code. You can grab a .zip from GitHub. 

### Dependancies

* Python 2.7
mox is untested with other versions of Python, it might work.
* git
Most of the current commands are git commands. There's probably a git package in your system's package management library. Something like `sudo apt-get install git`. 
*incron
This one isn't a strict dependency but it makes things much easier. Incron can run mox whenever a directory changes, this means you don't have to poll or run anything manually. The `mox_init` command assumes you have incrontab running because it adds the initialised directory to the incron table. 
* Dropbox
Again, not a strict dependency. I have mox monitor my Dropbox folders so I can makes changes in Dropbox and have them reflected in github. 

### Instructions

Here's how I setup my setup. I'm using a Debian VPS, you might have to change some of the commands to fit your environment. 

Create a new user, install some things

	$ sudo adduser 
	$ sudo apt-get install git incron
	
Become the new user and create some folders. One to keep Dropbox files in, one has a holding pen for git repos and one to keep the Dropbox script in. 

	$ su mox
	$ cd
	$ mkdir dropbox git bin
Now let's setup Dropbox, this will involve following the on screen instructions, it's pretty easy. 

	$ cd ~ && wget -O - "https://www.dropbox.com/download?plat=lnx.x86" | tar xzf -
	$ ~/.dropbox-dist/dropboxd
	$ cd bin
	$ wget https://linux.dropbox.com/packages/dropbox.py
Follow [this guide](https://help.github.com/articles/generating-ssh-keys) to create and assign some SSH keys for github.com. This way you don't have to type a password when interacting with github. 

Let's get mox and set up the configuration file. 

	$ wget https://codeload.github.com/WilliamMayor/mox/zip/master
	$ unzip mox-master.zip
	$ vim mox_config.txt
	dropbox_cli=/home/mox/bin/dropbox.py
	dropbox_root=/home/mox/dropbox
	git_root=/home/mox/git

We're nearly ready, let's tell incron to run mox when changes happen in the root of the Dropbox directory. This way we can clone projects. 

	$ incrontab -e
	/home/mox/dropbox IN_CLOSE_WRITE,IN_CREATE,IN_MOVED_TO python /home/mox/mox-master/mox.py /home/mox/mox_config.txt
OK, let's take her for a test drive

	$ vim /home/mox/dropbox/mox_clone
	git@github.com:WilliamMayor/mox.git

If everything works you'll see a git repository appear in `/home/mox/git` and the files in that repo will appear in your Dropbox account.
