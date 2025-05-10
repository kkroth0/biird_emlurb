import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  ChakraProvider, 
  Box, 
  Flex, 
  Heading, 
  Text,
  Tabs, 
  TabList, 
  TabPanels, 
  Tab, 
  TabPanel,
  Container,
  VStack,
  HStack,
  Badge,
  IconButton,
  useColorModeValue,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  Link as ChakraLink
} from '@chakra-ui/react';
import { FaMapMarkedAlt, FaTable, FaLink, FaGithub, FaChartBar, FaLock } from 'react-icons/fa';
import { HamburgerIcon } from '@chakra-ui/icons';

// Componentes
import WasteMonitoringMap from './components/Map';
import DetectionsTable from './components/DetectionsTable';
import DetectionDetails from './components/DetectionDetails';
import BlockchainViewer from './components/BlockchainViewer';

// Tema e estilos
import theme from './theme';

// Página inicial
function HomePage() {
  const [selectedDetection, setSelectedDetection] = useState(null);
  
  const handleStatusChange = (updatedDetection) => {
    setSelectedDetection(updatedDetection);
  };
  
  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading as="h1" size="xl">Monitoramento de Descarte Ilegal de Resíduos</Heading>
        
        <Tabs variant="enclosed" colorScheme="teal" isLazy>
          <TabList>
            <Tab><Box as={FaMapMarkedAlt} mr={2} /> Mapa</Tab>
            <Tab><Box as={FaTable} mr={2} /> Detecções</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel p={0} pt={4}>
              <Box mb={4}>
                <WasteMonitoringMap onSelectDetection={setSelectedDetection} />
              </Box>
              
              <Box mt={6}>
                <DetectionDetails 
                  detection={selectedDetection} 
                  onStatusChange={handleStatusChange} 
                />
              </Box>
            </TabPanel>
            
            <TabPanel p={0} pt={4}>
              <DetectionsTable onSelectDetection={setSelectedDetection} />
              
              <Box mt={6}>
                <DetectionDetails 
                  detection={selectedDetection} 
                  onStatusChange={handleStatusChange} 
                />
              </Box>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Container>
  );
}

// Página da Blockchain
function BlockchainPage() {
  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading as="h1" size="xl">
          <Box as={FaLock} display="inline-block" mr={2} />
          Auditoria e Transparência
        </Heading>
        <Text>
          Esta página permite visualizar o registro imutável de detecções de descarte ilegal
          na blockchain. Todos os eventos são registrados de forma permanente e verificável.
        </Text>
        
        <BlockchainViewer />
      </VStack>
    </Container>
  );
}

// Componente de Navegação
function Navigation({ mobileNav }) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const location = useLocation();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const isActive = (path) => location.pathname === path;
  
  const NavLinks = () => (
    <>
      <ChakraLink
        as={Link}
        to="/"
        px={4}
        py={2}
        rounded="md"
        fontWeight={isActive('/') ? 'bold' : 'normal'}
        bg={isActive('/') ? 'teal.50' : 'transparent'}
        color={isActive('/') ? 'teal.700' : 'inherit'}
        _hover={{ textDecoration: 'none', bg: 'teal.50' }}
      >
        <Flex align="center">
          <Box as={FaMapMarkedAlt} mr={2} />
          <Text>Dashboard</Text>
        </Flex>
      </ChakraLink>
      
      <ChakraLink
        as={Link}
        to="/blockchain"
        px={4}
        py={2}
        rounded="md"
        fontWeight={isActive('/blockchain') ? 'bold' : 'normal'}
        bg={isActive('/blockchain') ? 'teal.50' : 'transparent'}
        color={isActive('/blockchain') ? 'teal.700' : 'inherit'}
        _hover={{ textDecoration: 'none', bg: 'teal.50' }}
      >
        <Flex align="center">
          <Box as={FaLock} mr={2} />
          <Text>Blockchain</Text>
        </Flex>
      </ChakraLink>
    </>
  );
  
  return (
    <Box
      as="nav"
      position="sticky"
      top="0"
      zIndex="1000"
      bg={bgColor}
      borderBottom="1px"
      borderColor={borderColor}
      boxShadow="sm"
    >
      <Container maxW="container.xl">
        <Flex justify="space-between" align="center" py={3}>
          <Flex align="center">
            <Heading size="md" color="teal.500" mr={2}>EMLURB 2.0</Heading>
            <Badge colorScheme="green">POC</Badge>
          </Flex>
          
          {mobileNav ? (
            <>
              <IconButton
                aria-label="Abrir menu"
                icon={<HamburgerIcon />}
                onClick={onOpen}
                variant="ghost"
              />
              
              <Drawer isOpen={isOpen} placement="right" onClose={onClose}>
                <DrawerOverlay />
                <DrawerContent>
                  <DrawerCloseButton />
                  <DrawerHeader>Menu</DrawerHeader>
                  <DrawerBody>
                    <VStack align="stretch" spacing={4}>
                      <NavLinks />
                    </VStack>
                  </DrawerBody>
                </DrawerContent>
              </Drawer>
            </>
          ) : (
            <HStack spacing={4}>
              <NavLinks />
            </HStack>
          )}
        </Flex>
      </Container>
    </Box>
  );
}

// Componente de Rodapé
function Footer() {
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  return (
    <Box
      as="footer"
      borderTop="1px"
      borderColor={borderColor}
      py={6}
      mt={10}
    >
      <Container maxW="container.xl">
        <Flex 
          direction={{ base: "column", md: "row" }} 
          justify="space-between"
          align={{ base: "center", md: "center" }}
          textAlign={{ base: "center", md: "left" }}
        >
          <Box mb={{ base: 4, md: 0 }}>
            <Text fontSize="sm" color="gray.500">
              © 2023 EMLURB Recife - Monitoramento de Descarte Ilegal
            </Text>
            <Text fontSize="sm" color="gray.500">
              POC/MVP desenvolvido para demonstração de tecnologia
            </Text>
          </Box>
          
          <HStack spacing={4}>
            <ChakraLink href="https://github.com" isExternal color="gray.500">
              <Box as={FaGithub} />
            </ChakraLink>
            <ChakraLink href="https://recife.pe.gov.br" isExternal color="gray.500">
              <Box as={FaLink} />
            </ChakraLink>
          </HStack>
        </Flex>
      </Container>
    </Box>
  );
}

// Componente principal App
function App() {
  // Detectar se é mobile
  const isMobile = window.innerWidth < 768;
  
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <Box minH="100vh" display="flex" flexDirection="column">
          <Navigation mobileNav={isMobile} />
          
          <Box flex="1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/blockchain" element={<BlockchainPage />} />
            </Routes>
          </Box>
          
          <Footer />
        </Box>
      </Router>
    </ChakraProvider>
  );
}

export default App; 