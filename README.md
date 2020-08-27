# Focus Services - Python iTunes API Processor

Sample API evaluation project

## Dependencies for this project

`` Flask dependencies are installed with pip and the requirements.txt file``
- [flask](https://palletsprojects.com/p/flask/): Python server framework
- [flasgger](https://github.com/flasgger/flasgger): Used to generate the swagger documentation
- [flask-marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/): Flask serializer
- [apispec](https://apispec.readthedocs.io/en/latest/): Required for the integration between marshmallow and flasgger
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads/): Required to run the vagrant container
- [Vagrant](https://www.vagrantup.com/downloads/): Required to execute and provisioning the container

## Download the repository:
    - https://github.com/rbr8791/focuspythoneval.git
    
## Set Up - Run with Conda Environment

1. Download the conda environment for your O.S
    - [Conda] https://www.anaconda.com/products/individual
    - Install the package and make sure the binaries are in your PATH environment
2. Open a command prompt / bash shell window and execute the following commands in the root project directory:
    - 2.a ```pip install -r requirements``` (Install python dependencies for the project)
    - 2.b ```set the environment variables: ```
        - 2.b.1 for Windows:
            - set FLASK_APP=iap.py
            - set FLASK_ENV=development
            - set FLASK_DEBUG=1
        - 2.b.2 for *Nix:
            - export FLASK_APP=iap.py
            - export FLASK_ENV=development
            - export FLASK_DEBUG=1
3. Run the app:
    - ```flask run```
4. Open a web browser and navigate to http://localhost:5000/apidocs/#/

## Set Up - Run with a Vagrant container

1. Download the VirtualBox package and install it (Make sure the binaries are in your path)
2. Download the Vagrant package and install it (Make sure the binaries are in your path)
2. After VirtualBox and Vagrant were installed, go into the itunes-api-processor folder and execute the following commands:
    - 2.a ```vagrant up``` (Wait until the process completes)
    - 2.b ```vagrant halt```
    - 2.c ```vagrant plugin install vagrant-vbguest```
    - 2.d ```vagrant vbguest```
    - 2.e ```vagrant up``` (Wait until the container is up)
    - 2.f Open a web browser and navigate to http://localhost:5000/apidocs/#/

  
## API call samples

1. POST: /api/AddUser 
    - Add a new user to test the basic API authentication
    - Body data:
        - ```[{"username": "admin", "password": "admin", "email": "admin@domain.com", "access": "admin"}]```
2. GET: /api/deletePodCastById/{record_id}
    - Delete a stored PodCast from the SQLite database using the given record id
    - param:
        - record_id: The PodCast record id to delete
3. GET: /api/deletePodCastByName/{name}
    - Delete a stored PodCast from the SQLite database using the PodCast name
    - param:
        - name: The PodCast name
4. GET: /api/getPodCastByName/{name}
    - Get a stored PodCast using the name
    - param:
        - name: The PodCast name
5. GET: /api/getPodCasts
    - Call the iTunes API and get the top 100 PodCast, process the response and store the JSON data in a SQLite database
6. GET: /api/getUserById/{id}
    - Get a user by the given database Id
    - param:
        - id: The SQLite PodCast Id
7. POST: /api/login
    - Generate a token login (Bearer token auth is not yet implemented)
    - Body data:
        - `````[{"username": "admin", "password": "admin"}]`````
8. GET: /api/replaceTop20PodCastsWithBottom20
    - Switch Top 20 PodCasts with the Bottom 20 and output the results in a new JSON file
9. GET: /api/savePodCasts
    - Save the Top 100 iTunes PodCast into a new JSON file (output response is a file)
10. GET: /api/saveTop20PodCasts
    - Save the Top 20 stored PodCasts into a new JSON file (output response is a file)
11. GET: /api/welcome
    - Test the basic authentication method
    
## Author

R@ul Berrios
-
Rberrios@lifesize.com

