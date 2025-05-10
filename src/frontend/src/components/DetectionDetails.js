import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  Image,
  Badge,
  Divider,
  Button,
  Flex,
  Spinner,
  useToast,
  SimpleGrid,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure
} from '@chakra-ui/react';
import { FaCalendar, FaMapMarkerAlt, FaCamera, FaExclamationTriangle, FaCheck, FaLink, FaLock } from 'react-icons/fa';
import axios from 'axios';

// API URL
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const BLOCKCHAIN_URL = process.env.REACT_APP_BLOCKCHAIN_URL || 'http://localhost:8080';

function DetectionDetails({ detection, onStatusChange }) {
  const [loading, setLoading] = useState(false);
  const [blockchainData, setBlockchainData] = useState(null);
  const [blockchainLoading, setBlockchainLoading] = useState(false);
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();

  // Carregar dados da blockchain quando um detection for selecionado
  useEffect(() => {
    if (detection && detection.blockchain_hash) {
      fetchBlockchainData();
    } else {
      setBlockchainData(null);
    }
  }, [detection]);

  // Buscar dados da blockchain
  const fetchBlockchainData = async () => {
    if (!detection) return;
    
    setBlockchainLoading(true);
    try {
      const response = await axios.get(`${API_URL}/blockchain/detection/${detection.id}`);
      setBlockchainData(response.data);
    } catch (error) {
      console.error('Erro ao carregar dados da blockchain:', error);
      setBlockchainData(null);
    } finally {
      setBlockchainLoading(false);
    }
  };

  // Atualizar o status da detecção
  const updateStatus = async (newStatus) => {
    if (!detection) return;
    
    setLoading(true);
    try {
      await axios.put(`${API_URL}/waste-detections/${detection.id}`, {
        status: newStatus
      });
      
      toast({
        title: 'Status atualizado',
        description: `Status alterado para ${newStatus}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // Atualizar localmente
      const updatedDetection = { ...detection, status: newStatus };
      
      // Notificar o componente pai
      if (onStatusChange) {
        onStatusChange(updatedDetection);
      }
      
      // Recarregar dados da blockchain se necessário
      if (newStatus === "Em Atendimento") {
        setTimeout(fetchBlockchainData, 1000);
      }
      
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      toast({
        title: 'Erro',
        description: 'Não foi possível atualizar o status.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  // Enviar notificação manual
  const sendNotification = async () => {
    if (!detection) return;
    
    setLoading(true);
    try {
      await axios.post(`${API_URL}/notifications`, {
        detection_id: detection.id,
        recipients: ["5511999999999"] // Em um app real, seria uma lista configurável
      });
      
      toast({
        title: 'Notificação enviada',
        description: 'Notificação enviada com sucesso aos fiscais.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Erro ao enviar notificação:', error);
      toast({
        title: 'Erro',
        description: 'Não foi possível enviar a notificação.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  if (!detection) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="lg" bg="white" boxShadow="sm">
        <Text textAlign="center" color="gray.500">
          Selecione uma detecção no mapa ou na tabela para ver os detalhes.
        </Text>
      </Box>
    );
  }

  return (
    <Box p={4} borderWidth="1px" borderRadius="lg" bg="white" boxShadow="sm">
      <Heading size="md" mb={4}>
        Detecção de Descarte Ilegal
        <Badge 
          ml={2} 
          colorScheme={
            detection.status === "Aberto" ? "red" : 
            detection.status === "Em Atendimento" ? "yellow" : 
            "green"
          }
        >
          {detection.status}
        </Badge>
      </Heading>
      
      <Divider mb={4} />
      
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
        <Box>
          <Flex align="center" mb={2}>
            <Box as={FaCalendar} mr={2} color="blue.500" />
            <Text fontWeight="bold">Data/Hora:</Text>
            <Text ml={2}>{new Date(detection.timestamp).toLocaleString()}</Text>
          </Flex>
          
          <Flex align="center" mb={2}>
            <Box as={FaMapMarkerAlt} mr={2} color="red.500" />
            <Text fontWeight="bold">Localização:</Text>
            <Text ml={2}>
              {detection.coordinates.latitude.toFixed(4)}, {detection.coordinates.longitude.toFixed(4)}
            </Text>
          </Flex>
          
          <Flex align="center" mb={2}>
            <Box as={FaCamera} mr={2} color="teal.500" />
            <Text fontWeight="bold">Câmera:</Text>
            <Text ml={2}>{detection.camera_id}</Text>
          </Flex>
          
          <Flex align="center" mb={2}>
            <Box as={FaExclamationTriangle} mr={2} color="orange.500" />
            <Text fontWeight="bold">Tipo de Resíduo:</Text>
            <Text ml={2}>{detection.waste_type || "Desconhecido"}</Text>
          </Flex>
          
          {detection.blockchain_hash && (
            <Flex align="center" mb={2}>
              <Box as={FaLock} mr={2} color="purple.500" />
              <Text fontWeight="bold">Hash Blockchain:</Text>
              <Text ml={2} fontSize="sm" isTruncated maxW="200px">
                {detection.blockchain_hash}
              </Text>
              <Button 
                size="xs" 
                colorScheme="purple" 
                variant="outline" 
                ml={2}
                onClick={onOpen}
              >
                Ver
              </Button>
            </Flex>
          )}
        </Box>
        
        <Box>
          {detection.image_url ? (
            <Image 
              src={`${API_URL.replace('/api', '')}${detection.image_url}`}
              alt="Imagem da detecção"
              borderRadius="md"
              maxH="200px"
              mx="auto"
            />
          ) : (
            <Alert status="info">
              <AlertIcon />
              <AlertTitle>Sem imagem</AlertTitle>
              <AlertDescription>Esta detecção não possui imagem associada.</AlertDescription>
            </Alert>
          )}
        </Box>
      </SimpleGrid>
      
      <Divider my={4} />
      
      <Flex justify="space-between" wrap="wrap" gap={2}>
        {detection.status === "Aberto" && (
          <Button 
            leftIcon={<FaCheck />}
            colorScheme="yellow"
            onClick={() => updateStatus("Em Atendimento")}
            isLoading={loading}
          >
            Marcar Em Atendimento
          </Button>
        )}
        
        {detection.status === "Em Atendimento" && (
          <Button 
            leftIcon={<FaCheck />}
            colorScheme="green"
            onClick={() => updateStatus("Concluído")}
            isLoading={loading}
          >
            Marcar como Concluído
          </Button>
        )}
        
        <Button 
          leftIcon={<FaLink />}
          colorScheme="blue"
          onClick={sendNotification}
          isLoading={loading}
        >
          Reenviar Notificação
        </Button>
      </Flex>
      
      {/* Modal para exibir dados da blockchain */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Registro Blockchain</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {blockchainLoading ? (
              <Flex justify="center" align="center" p={10}>
                <Spinner size="xl" />
              </Flex>
            ) : blockchainData ? (
              <Box>
                <SimpleGrid columns={2} spacing={4} mb={4}>
                  <Box>
                    <Text fontWeight="bold">Índice do Bloco:</Text>
                    <Text>{blockchainData.index}</Text>
                  </Box>
                  <Box>
                    <Text fontWeight="bold">Hash:</Text>
                    <Text fontSize="sm" isTruncated>{blockchainData.hash}</Text>
                  </Box>
                  <Box>
                    <Text fontWeight="bold">Hash Anterior:</Text>
                    <Text fontSize="sm" isTruncated>{blockchainData.previous_hash}</Text>
                  </Box>
                  <Box>
                    <Text fontWeight="bold">Timestamp:</Text>
                    <Text>{new Date(blockchainData.timestamp * 1000).toLocaleString()}</Text>
                  </Box>
                </SimpleGrid>
                
                <Heading size="sm" mb={2}>Dados do Bloco:</Heading>
                <Box 
                  p={3} 
                  borderWidth="1px" 
                  borderRadius="md" 
                  bg="gray.50" 
                  fontSize="sm"
                  overflowX="auto"
                >
                  <pre>{JSON.stringify(blockchainData.data, null, 2)}</pre>
                </Box>
              </Box>
            ) : (
              <Alert status="warning">
                <AlertIcon />
                <AlertTitle>Dados não encontrados</AlertTitle>
                <AlertDescription>
                  Não foi possível encontrar um registro na blockchain para esta detecção.
                </AlertDescription>
              </Alert>
            )}
          </ModalBody>

          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onClose}>
              Fechar
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}

export default DetectionDetails; 