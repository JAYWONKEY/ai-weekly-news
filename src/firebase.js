// src/firebase.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyBYvLz57AHG7g3owtYDKzDS-jhyTAXkx6Q",
  authDomain: "aiweeklynews.firebaseapp.com",
  projectId: "aiweeklynews",
  storageBucket: "aiweeklynews.firebasestorage.app",
  messagingSenderId: "607506672486",
  appId: "1:607506672486:web:955faf6754430b548776a7",
  measurementId: "G-TVRQZ0R88G"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore Database
export const db = getFirestore(app);