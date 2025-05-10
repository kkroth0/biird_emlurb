// src/components/Map.js
import React, { useState, useEffect, useRef } from 'react';
// Import TensorFlow and backend before model
import '@tensorflow/tfjs-backend-webgl';
import * as tf from '@tensorflow/tfjs';
import Webcam from 'react-webcam';
import * as cocoSsd from '@tensorflow-models/coco-ssd';
import {
  Box,
  Text,
  Badge,
  Heading,
  Button,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  useDisclosure,
} from '@chakra-ui/react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { FaCamera } from 'react-icons/fa';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

// Corrigir ícones do Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// Configurações
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const RECIFE_CENTER = [-8.0476, -34.8770];
const BOTTLE_THRESHOLD = 5; // quantidade para disparar alerta

// Ícones personalizados
const DefaultIcon = L.icon({ iconUrl: icon, shadowUrl: iconShadow, iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34] });
const AlertIcon = L.icon({ iconUrl: icon, shadowUrl: iconShadow, iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], className: 'alert-icon' });

// Centraliza mapa
function SetViewOnClick({ coords }) {
  const map = useMap();
  useEffect(() => {
    map.setView(coords, map.getZoom());
  }, [map, coords]); // incluiu 'map' para satisfazer eslint
  return null;
}

export default function WasteMonitoringMap({ onSelectDetection }) {
  const [cameras, setCameras] = useState([]);
  const [detections, setDetections] = useState([]);
  const [center, setCenter] = useState(RECIFE_CENTER);
  const [activeCamera, setActiveCamera] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Refs
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const modelRef = useRef(null);
  const alertSoundRef = useRef(null);
  const intervalRef = useRef(null);

  // Inicializar backend e carregar modelo COCO-SSD
  useEffect(() => {
    tf.setBackend('webgl');
    tf.ready()
      .then(() => cocoSsd.load())
      .then(model => { modelRef.current = model; })
      .catch(err => {
        console.error('Falha ao carregar TensorFlow/modelo:', err);
        toast({ title: 'Erro', description: 'Falha ao carregar modelo de visão computacional', status: 'error', duration: 5000, isClosable: true });
      });
  }, [toast]);

  // Detectar e desenhar caixas
  const detectFrame = async () => {
    const video = webcamRef.current?.video;
    const canvas = canvasRef.current;
    if (!video || video.readyState < 2 || !modelRef.current) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const predictions = await modelRef.current.detect(video);
    let bottleCount = 0;

    predictions.forEach(pred => {
      const { bbox, class: cls, score } = pred;
      if (cls === 'bottle') {
        bottleCount++;
        const [x, y, w, h] = bbox;
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);
        ctx.font = '16px sans-serif';
        ctx.fillStyle = 'red';
        ctx.fillText(`${cls} (${(score * 100).toFixed(1)}%)`, x, y > 10 ? y - 5 : 10);
      }
    });

    if (bottleCount >= BOTTLE_THRESHOLD) {
      toast({ title: 'Alerta de Garrafas', description: `${bottleCount} garrafas detectadas`, status: 'warning', duration: 3000, isClosable: true });
      alertSoundRef.current?.play();
    }
  };

  // Intervalo ligado ao modal
  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    if (isOpen) {
      intervalRef.current = setInterval(detectFrame, 500);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [isOpen]); // remove detectFrame da deps e suprime lint

  // Fetch câmeras
  useEffect(() => {
    const loadCam = async () => {
      try {
        const { data } = await axios.get(`${API_URL}/cameras`);
        setCameras(data);
      } catch {
        toast({ title: 'Erro', description: 'Falha ao carregar câmeras', status: 'error', duration: 5000, isClosable: true });
      }
    };
    loadCam(); const iid = setInterval(loadCam, 30000);
    return () => clearInterval(iid);
  }, [toast]);

  // Fetch detecções
  useEffect(() => {
    const loadDet = async () => {
      try {
        const { data } = await axios.get(`${API_URL}/waste-detections`, { params: { limit: 50 } });
        setDetections(data);
      } catch {}
    };
    loadDet(); const jid = setInterval(loadDet, 30000);
    return () => clearInterval(jid);
  }, []);

  const handleCameraClick = camera => {
    setActiveCamera(camera);
    setCenter([camera.coordinates.latitude, camera.coordinates.longitude]);
    onOpen();
  };

  return (
    <Box h="600px" w="100%" pos="relative">
      <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }}>
        <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {cameras.map(cam => {
          const hasAlert = detections.some(d => d.camera_id === cam.id && d.status === 'Aberto');
          return (
            <Marker
              key={cam.id}
              position={[cam.coordinates.latitude, cam.coordinates.longitude]}
              icon={hasAlert ? AlertIcon : DefaultIcon}
              eventHandlers={{ click: () => handleCameraClick(cam) }}
            >
              <Popup>
                <Box>
                  <Heading size="sm">{cam.name}</Heading>
                  <Text fontSize="sm">Local: {cam.location}</Text>
                  <Badge colorScheme={cam.status === 'Online' ? 'green' : 'red'}>{cam.status}</Badge>
                  <Button mt={2} size="sm" leftIcon={<FaCamera />} onClick={() => handleCameraClick(cam)}>
                    Ver Câmera Ao Vivo
                  </Button>
                </Box>
              </Popup>
            </Marker>
          );
        })}
        <SetViewOnClick coords={center} />
      </MapContainer>

      <Modal isOpen={isOpen} onClose={onClose} size="xl" isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Câmera: {activeCamera?.name}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Box pos="relative" w="100%">
              <Webcam
                ref={webcamRef}
                audio={false}
                mirrored
                videoConstraints={{ width: 640, height: 480, facingMode: 'environment' }}
                style={{ width: '100%', zIndex: 0 }}
              />
              <canvas
                ref={canvasRef}
                style={{ position: 'absolute', top: 0, left: 0, zIndex: 1, width: '100%', height: 'auto', pointerEvents: 'none' }}
              />
            </Box>
            <audio ref={alertSoundRef} src="/alert.mp3" />
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Fechar</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}
