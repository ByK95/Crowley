# 🕷️ Crowley

Web page that collects data from websites.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Things you need to install the software and how to install them
- [Python 3.6 or above](https://www.python.org/downloads/)
- Pip ( Comes pre-installed with python )
- Virtualenv
```
#Clone this repository
git clone https://github.com/ByK95/cs50final

cd cs50final

python -m pip install --user virtualenv
or
pip install virtualenv

#Create virtual environment
virtualenv env

```

#### Activate virtual environment

Mac OS / Linux
```
source mypython/bin/activate
```

Windows
```
env\Scripts\activate
```

Windows(MINGW)
```
source env/Scripts/activate
```

### Installing

Install dependencies

```
pip install -r requirements.txt
```

Create database and schemas

```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

Start development server

```
python manage.py runserver --host 0.0.0.0 --port 5000
```

End with an example of getting some data out of the system or using it for a little demo


## Deployment

Production copy works in Heroku [Link](https://bykcs50final.herokuapp.com/)

How to setup database [Link](https://gist.github.com/mayukh18/2223bc8fc152631205abd7cbf1efdd41)

## Built With ☕

## Contributing

Any contribution is welcome.

## Author

* **Bayram Kaya**