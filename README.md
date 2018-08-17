# Udacity Item Catalog

Web application that provides a list of items within a variety of categories and integrate Google Account user registration and authentication. 

## Set Up

1. Clone the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).

2. Copy the folder content to the folder `catalog`

3. 

## Usage

Launch the Vagrant VM from inside the *vagrant* folder with:

`vagrant up`

Then move inside the catalog folder:

`cd /vagrant/catalog`

Set up the database:

`python database_setup.py`

Add dummy items to the database:

`python gameslist.py`

Then run the application:

`python project.py`

After the last command you are able to browse the application at this URL:

`http://localhost:5001/`


