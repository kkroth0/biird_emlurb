import React, { useState, useEffect, useMemo } from 'react';
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Box,
  Badge,
  Button,
  Flex,
  Text,
  Select,
  Input,
  InputGroup,
  InputLeftElement,
  Spinner,
  useToast
} from '@chakra-ui/react';
import { FaSearch, FaFilter, FaEye } from 'react-icons/fa';
import axios from 'axios';

// API URL
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function DetectionsTable({ onSelectDetection }) {
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [cameraFilter, setCameraFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [cameras, setCameras] = useState([]);
  const toast = useToast();

  // Carregar todas as detecções
  useEffect(() => {
    const fetchDetections = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_URL}/waste-detections`, {
          params: { limit: 100 }
        });
        setDetections(response.data);
      } catch (error) {
        console.error('Erro ao carregar detecções:', error);
        toast({
          title: 'Erro',
          description: 'Não foi possível carregar as detecções.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDetections();
    // Atualizar a cada 60 segundos
    const interval = setInterval(fetchDetections, 60000);
    
    return () => clearInterval(interval);
  }, [toast]);

  // Carregar lista de câmeras para o filtro
  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const response = await axios.get(`${API_URL}/cameras`);
        setCameras(response.data);
      } catch (error) {
        console.error('Erro ao carregar câmeras:', error);
      }
    };

    fetchCameras();
  }, []);

  // Aplicar filtros à lista de detecções
  const filteredDetections = useMemo(() => {
    return detections.filter(detection => {
      // Filtro por status
      if (statusFilter && detection.status !== statusFilter) {
        return false;
      }
      
      // Filtro por câmera
      if (cameraFilter && detection.camera_id !== cameraFilter) {
        return false;
      }
      
      // Busca por texto (ID, tipo de resíduo, hash da blockchain)
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          detection.id.toLowerCase().includes(query) ||
          (detection.waste_type && detection.waste_type.toLowerCase().includes(query)) ||
          (detection.blockchain_hash && detection.blockchain_hash.toLowerCase().includes(query))
        );
      }
      
      return true;
    });
  }, [detections, statusFilter, cameraFilter, searchQuery]);

  // Formatar data
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <Box borderWidth="1px" borderRadius="lg" overflow="hidden" bg="white">
      <Box p={4} borderBottomWidth="1px" bg="gray.50">
        <Flex direction={{ base: 'column', md: 'row' }} gap={3}>
          <InputGroup maxW={{ base: '100%', md: '300px' }}>
            <InputLeftElement pointerEvents="none">
              <FaSearch color="gray.300" />
            </InputLeftElement>
            <Input 
              placeholder="Buscar detecções..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </InputGroup>
          
          <Select 
            placeholder="Filtrar por status" 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            maxW={{ base: '100%', md: '200px' }}
          >
            <option value="Aberto">Aberto</option>
            <option value="Em Atendimento">Em Atendimento</option>
            <option value="Concluído">Concluído</option>
          </Select>
          
          <Select 
            placeholder="Filtrar por câmera" 
            value={cameraFilter}
            onChange={(e) => setCameraFilter(e.target.value)}
            maxW={{ base: '100%', md: '200px' }}
          >
            {cameras.map(camera => (
              <option key={camera.id} value={camera.id}>
                {camera.name}
              </option>
            ))}
          </Select>
          
          <Button 
            leftIcon={<FaFilter />}
            onClick={() => {
              setStatusFilter('');
              setCameraFilter('');
              setSearchQuery('');
            }}
            colorScheme="blue"
            variant="outline"
          >
            Limpar Filtros
          </Button>
        </Flex>
      </Box>
      
      {loading ? (
        <Flex justify="center" align="center" p={10}>
          <Spinner size="xl" />
        </Flex>
      ) : (
        <>
          <Box overflowX="auto">
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th>Data/Hora</Th>
                  <Th>Câmera</Th>
                  <Th>Tipo de Resíduo</Th>
                  <Th>Status</Th>
                  <Th>Blockchain</Th>
                  <Th>Ações</Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredDetections.length > 0 ? (
                  filteredDetections.map(detection => (
                    <Tr key={detection.id}>
                      <Td>{formatDate(detection.timestamp)}</Td>
                      <Td>{detection.camera_id}</Td>
                      <Td>{detection.waste_type || "Desconhecido"}</Td>
                      <Td>
                        <Badge 
                          colorScheme={
                            detection.status === "Aberto" ? "red" : 
                            detection.status === "Em Atendimento" ? "yellow" : 
                            "green"
                          }
                        >
                          {detection.status}
                        </Badge>
                      </Td>
                      <Td>
                        {detection.blockchain_hash ? (
                          <Badge colorScheme="purple">Registrado</Badge>
                        ) : (
                          <Badge colorScheme="gray">Pendente</Badge>
                        )}
                      </Td>
                      <Td>
                        <Button
                          leftIcon={<FaEye />} 
                          size="sm"
                          colorScheme="teal"
                          onClick={() => onSelectDetection(detection)}
                        >
                          Detalhes
                        </Button>
                      </Td>
                    </Tr>
                  ))
                ) : (
                  <Tr>
                    <Td colSpan={6} textAlign="center" py={4}>
                      Nenhuma detecção encontrada com os filtros atuais.
                    </Td>
                  </Tr>
                )}
              </Tbody>
            </Table>
          </Box>
          
          <Box p={4} borderTopWidth="1px" bg="gray.50">
            <Text>
              Exibindo {filteredDetections.length} de {detections.length} detecções
            </Text>
          </Box>
        </>
      )}
    </Box>
  );
}

export default DetectionsTable; 