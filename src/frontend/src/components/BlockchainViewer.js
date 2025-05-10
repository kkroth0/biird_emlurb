import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Button,
  Flex,
  Spinner,
  useToast,
  Collapse,
  SimpleGrid,
  Divider,
  Icon,
  Alert,
  AlertIcon,
  useColorModeValue
} from '@chakra-ui/react';
import { FaCheck, FaLink, FaLock, FaUnlock, FaChevronDown, FaChevronUp } from 'react-icons/fa';
import axios from 'axios';

// API URL
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function BlockchainViewer() {
  const [chain, setChain] = useState([]);
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const [isValid, setIsValid] = useState(null);
  const [expandedBlock, setExpandedBlock] = useState(null);
  const toast = useToast();
  
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const bgColor = useColorModeValue('white', 'gray.800');

  // Carregar a blockchain
  useEffect(() => {
    const fetchBlockchain = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_URL}/blockchain/chain`);
        setChain(response.data);
      } catch (error) {
        console.error('Erro ao carregar blockchain:', error);
        toast({
          title: 'Erro',
          description: 'Não foi possível carregar a blockchain.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchBlockchain();
  }, [toast]);

  // Validar a blockchain
  const validateBlockchain = async () => {
    setValidating(true);
    try {
      const response = await axios.get(`${API_URL}/blockchain/validate`);
      setIsValid(response.data.valid);
      
      toast({
        title: response.data.valid ? 'Blockchain Válida' : 'Blockchain Inválida',
        description: response.data.valid 
          ? 'A blockchain foi verificada e está íntegra.' 
          : 'A verificação falhou. A blockchain pode ter sido adulterada.',
        status: response.data.valid ? 'success' : 'error',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Erro ao validar blockchain:', error);
      toast({
        title: 'Erro',
        description: 'Não foi possível validar a blockchain.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setValidating(false);
    }
  };

  // Expandir/recolher um bloco
  const toggleBlock = (index) => {
    if (expandedBlock === index) {
      setExpandedBlock(null);
    } else {
      setExpandedBlock(index);
    }
  };

  // Formatar data
  const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Blockchain de Registros Imutáveis</Heading>
        <Button 
          leftIcon={isValid ? <FaCheck /> : <FaLink />}
          colorScheme={isValid ? "green" : "blue"}
          onClick={validateBlockchain}
          isLoading={validating}
        >
          Verificar Integridade
        </Button>
      </Flex>
      
      {isValid !== null && (
        <Alert 
          status={isValid ? "success" : "error"} 
          mb={6}
          borderRadius="md"
        >
          <AlertIcon />
          {isValid 
            ? "Blockchain verificada com sucesso! Todos os registros estão íntegros." 
            : "Atenção! A blockchain apresenta inconsistências e pode ter sido adulterada."
          }
        </Alert>
      )}
      
      {loading ? (
        <Flex justify="center" align="center" p={10}>
          <Spinner size="xl" />
        </Flex>
      ) : (
        <VStack spacing={4} align="stretch">
          {chain.map((block, index) => (
            <Box 
              key={block.hash} 
              borderWidth="1px" 
              borderRadius="lg" 
              overflow="hidden"
              borderColor={borderColor}
              bg={bgColor}
              boxShadow="sm"
            >
              <Flex 
                p={4} 
                cursor="pointer" 
                onClick={() => toggleBlock(index)}
                justify="space-between"
                align="center"
                bg={index === 0 ? "purple.50" : "transparent"}
              >
                <HStack>
                  <Icon as={block.hash.startsWith('00') ? FaLock : FaUnlock} 
                        color={block.hash.startsWith('00') ? "green.500" : "orange.500"} 
                  />
                  <Text fontWeight="bold">
                    Bloco #{block.index}
                    {index === 0 && (
                      <Badge ml={2} colorScheme="purple">Gênesis</Badge>
                    )}
                  </Text>
                  <Text color="gray.500" fontSize="sm">
                    {formatDate(block.timestamp)}
                  </Text>
                </HStack>
                <Icon as={expandedBlock === index ? FaChevronUp : FaChevronDown} />
              </Flex>
              
              <Collapse in={expandedBlock === index}>
                <Box p={4} borderTopWidth="1px" borderColor={borderColor}>
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mb={4}>
                    <Box>
                      <Text fontWeight="bold" fontSize="sm" color="gray.500">Hash:</Text>
                      <Text fontSize="sm" fontFamily="monospace" overflowWrap="break-word">
                        {block.hash}
                      </Text>
                    </Box>
                    
                    <Box>
                      <Text fontWeight="bold" fontSize="sm" color="gray.500">Hash Anterior:</Text>
                      <Text fontSize="sm" fontFamily="monospace" overflowWrap="break-word">
                        {block.previous_hash}
                      </Text>
                    </Box>
                  </SimpleGrid>
                  
                  <Divider my={4} />
                  
                  <Text fontWeight="bold" fontSize="sm" color="gray.500" mb={2}>
                    Dados do Bloco:
                  </Text>
                  <Box 
                    p={3} 
                    borderWidth="1px" 
                    borderRadius="md" 
                    bg="gray.50" 
                    fontSize="sm"
                    fontFamily="monospace"
                    overflowX="auto"
                    maxH="200px"
                    overflowY="auto"
                  >
                    <pre>{JSON.stringify(block.data, null, 2)}</pre>
                  </Box>
                  
                  {block.data.detection_id && (
                    <Flex mt={4} justify="flex-end">
                      <Button 
                        size="sm" 
                        colorScheme="blue" 
                        leftIcon={<FaLink />}
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(`/detections/${block.data.detection_id}`, '_blank');
                        }}
                      >
                        Ver Detecção
                      </Button>
                    </Flex>
                  )}
                </Box>
              </Collapse>
            </Box>
          ))}
        </VStack>
      )}
      
      {chain.length === 0 && !loading && (
        <Box textAlign="center" p={10}>
          <Text>Nenhum bloco encontrado na blockchain. O sistema ainda não registrou eventos.</Text>
        </Box>
      )}
    </Box>
  );
}

export default BlockchainViewer; 