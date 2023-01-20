// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here. Other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/8.2.6/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.2.6/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
var firebaseConfig = {
    apiKey: "AIzaSyBAxox30pwqqcR4XmdGQepPiqqU33kwvEw",
    authDomain: "wwf-notifications.firebaseapp.com",
    projectId: "wwf-notifications",
    storageBucket: "wwf-notifications.appspot.com",
    messagingSenderId: "978859121425",
    appId: "1:978859121425:web:49ea3fa32e7109e3028ab0",
    measurementId: "G-FD90C11TV8"
};
firebase.initializeApp(firebaseConfig);

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  // Customize notification here
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/img/wwf_logo.png'
  };


  self.registration.showNotification(notificationTitle,
    notificationOptions);
});
