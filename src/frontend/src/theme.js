import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  colors: {
    brand: {
      50: '#e6f5ff',
      100: '#b3e0ff',
      200: '#80ccff',
      300: '#4db8ff',
      400: '#1aa3ff',
      500: '#0080e6',
      600: '#0066b3',
      700: '#004d80',
      800: '#00334d',
      900: '#001a26',
    },
  },
  fonts: {
    heading: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
    body: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
  },
  styles: {
    global: {
      body: {
        bg: 'gray.50',
      },
    },
  },
  components: {
    Button: {
      defaultProps: {
        colorScheme: 'teal',
      },
    },
    Tabs: {
      defaultProps: {
        colorScheme: 'teal',
      },
    },
    Table: {
      variants: {
        simple: {
          th: {
            bg: 'gray.50',
          },
        },
      },
    },
  },
});

export default theme; 