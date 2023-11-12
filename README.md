# Digits

This web app is designed for classifying images of digits. Submit an image containing a single digit, and the app will identify and tell you which digit is present.

The underlying model was trained on the MNIST dataset with 13 epochs. Training was stopped after the maximum accuracy did not improve for 5 consecutive epochs. The training was performed on Google Colab.

- Training Accuracy: 99.86875
- Test Accuracy: 99.5

The scripts related to neural networks are located within the app/digits/neural directory.

## Running with Docker

To run the project with Docker, navigate to the 'app' folder (the folder containing the Dockerfile) and execute the following commands:

```bash
docker build -t digits .
docker run -d --name digits-container -p 8000:8000 digits
```

The app should now be running, and you can access it at http://localhost:8000 in your web browser.

## Running with Django
To run the app using Django, navigate to the 'app' folder (the folder containing manage.py) and execute the following command:

```bash
python manage.py runserver
```

Make sure you have all the required dependencies listed in requirements.txt, otherwise, the app may not work properly.
