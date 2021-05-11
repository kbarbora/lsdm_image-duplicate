# Image Duplicate Detection Back-End

Back end python scripts for the image duplicate detection project.

It uses [Image Deduplicator](https://idealo.github.io/imagededup/) framework to detect images. Since the Hashing mechanism performs really good
and because limited computational resources (GPU) is the only algorithm implemented.

##Install and Requirements

Python 3.7 and newer

All the dependencies needed are in "requirements.txt"

##Command Line Arguments and Usage
```
python3 duplicate_detection [-h] --dir DIR [--debug] [--recursive] [--delete]
                           [--log] [--outputimage]

optional arguments:
  -h, --help          show this help message and exit
  --dir DIR           The directory where the images are located
  --debug             Enable debug mode
  --recursive, -r     Do a recursive search, traversing through all
                      directories inside.
  --delete            Delete all the duplicates found without asking the user.
  --log               Log to file 'image_detection.log' in append mode instead
                      to STDIN
  --outputimage, -oi  Produce an output image showing the possible duplicates
```

###Author and Acknowledgement
Group Members: Oscar Falcon, Nicole Jenkins, Kevin Barba

Author: Kevin Barba

Class: Large Scale Data Managment 

Professor: Dr Arora Ritu

Spring 2021

University of Texas at San Antonio

###License
[MIT](https://choosealicense.com/licenses/mit/)