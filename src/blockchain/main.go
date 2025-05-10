package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

// Block representa um bloco na blockchain
type Block struct {
	Index        int         `json:"index"`
	Timestamp    int64       `json:"timestamp"`
	Data         interface{} `json:"data"`
	PreviousHash string      `json:"previous_hash"`
	Hash         string      `json:"hash"`
	Nonce        int         `json:"nonce"`
}

// Blockchain representa a cadeia de blocos
type Blockchain struct {
	Chain  []Block    `json:"chain"`
	mutex  sync.Mutex // para acesso concorrente seguro
	dbPath string     // caminho para o arquivo da blockchain
}

// MineRequest representa a solicitação para minerar um novo bloco
type MineRequest struct {
	Data interface{} `json:"data"`
}

// MineResponse representa a resposta da mineração de um bloco
type MineResponse struct {
	Message string `json:"message"`
	Index   int    `json:"index"`
	Hash    string `json:"hash"`
}

// ValidateResponse representa a resposta da validação da blockchain
type ValidateResponse struct {
	Valid bool `json:"valid"`
}

// Novo blockchain com bloco gênesis
func NewBlockchain(dbPath string) *Blockchain {
	bc := &Blockchain{
		Chain:  []Block{},
		dbPath: dbPath,
	}

	// Tentar carregar a blockchain existente
	err := bc.loadFromFile()
	if err != nil || len(bc.Chain) == 0 {
		// Se não conseguir carregar ou estiver vazia, criar bloco gênesis
		log.Println("Criando blockchain com bloco gênesis")
		genesisData := map[string]interface{}{
			"message": "Bloco Gênesis da Blockchain de Monitoramento de Descarte Ilegal",
			"creator": "EMLURB Recife",
			"date":    time.Now().Format(time.RFC3339),
		}
		bc.createGenesisBlock(genesisData)
		// Salvar a blockchain
		bc.saveToFile()
	}

	return bc
}

// Cria o bloco gênesis
func (bc *Blockchain) createGenesisBlock(data interface{}) {
	bc.mutex.Lock()
	defer bc.mutex.Unlock()

	genesisBlock := Block{
		Index:        0,
		Timestamp:    time.Now().Unix(),
		Data:         data,
		PreviousHash: "0",
		Nonce:        0,
	}

	// Minerar o bloco gênesis com dificuldade zero para simplicidade
	genesisBlock.Hash = bc.calculateHash(genesisBlock)
	bc.Chain = append(bc.Chain, genesisBlock)
}

// Calcula o hash SHA256 de um bloco
func (bc *Blockchain) calculateHash(block Block) string {
	blockData, _ := json.Marshal(block.Data)
	record := strconv.Itoa(block.Index) +
		strconv.FormatInt(block.Timestamp, 10) +
		string(blockData) +
		block.PreviousHash +
		strconv.Itoa(block.Nonce)

	h := sha256.New()
	h.Write([]byte(record))
	hashed := h.Sum(nil)
	return hex.EncodeToString(hashed)
}

// Adiciona um novo bloco à blockchain com proof of work simples
func (bc *Blockchain) addBlock(data interface{}) Block {
	bc.mutex.Lock()
	defer bc.mutex.Unlock()

	lastBlock := bc.Chain[len(bc.Chain)-1]
	newBlock := Block{
		Index:        lastBlock.Index + 1,
		Timestamp:    time.Now().Unix(),
		Data:         data,
		PreviousHash: lastBlock.Hash,
		Nonce:        0,
	}

	// Proof of Work simples com dificuldade 2 (começa com "00")
	difficulty := 2
	target := strings.Repeat("0", difficulty)

	for {
		newBlock.Hash = bc.calculateHash(newBlock)
		if newBlock.Hash[:difficulty] == target {
			break
		}
		newBlock.Nonce++
	}

	bc.Chain = append(bc.Chain, newBlock)
	bc.saveToFile()

	return newBlock
}

// Verifica se a blockchain é válida
func (bc *Blockchain) isValid() bool {
	bc.mutex.Lock()
	defer bc.mutex.Unlock()

	for i := 1; i < len(bc.Chain); i++ {
		currentBlock := bc.Chain[i]
		previousBlock := bc.Chain[i-1]

		// Verificar se o hash do bloco atual é válido
		if currentBlock.Hash != bc.calculateHash(currentBlock) {
			return false
		}

		// Verificar se o campo previousHash do bloco atual aponta para o hash do bloco anterior
		if currentBlock.PreviousHash != previousBlock.Hash {
			return false
		}
	}
	return true
}

// Busca um bloco pelo hash
func (bc *Blockchain) getBlockByHash(hash string) (Block, bool) {
	bc.mutex.Lock()
	defer bc.mutex.Unlock()

	for _, block := range bc.Chain {
		if block.Hash == hash {
			return block, true
		}
	}
	return Block{}, false
}

// Busca um bloco pelos dados (para POC simplificado)
func (bc *Blockchain) searchBlockByDetectionID(detectionID string) (Block, bool) {
	bc.mutex.Lock()
	defer bc.mutex.Unlock()

	for i := len(bc.Chain) - 1; i >= 0; i-- {
		block := bc.Chain[i]
		blockDataJSON, err := json.Marshal(block.Data)
		if err != nil {
			continue
		}

		var blockData map[string]interface{}
		err = json.Unmarshal(blockDataJSON, &blockData)
		if err != nil {
			continue
		}

		// Verificar se o campo detection_id existe e corresponde ao ID procurado
		if id, exists := blockData["detection_id"]; exists && id == detectionID {
			return block, true
		}
	}
	return Block{}, false
}

// Salva a blockchain em um arquivo JSON
func (bc *Blockchain) saveToFile() error {
	data, err := json.Marshal(bc.Chain)
	if err != nil {
		return err
	}

	return os.WriteFile(bc.dbPath, data, 0644)
}

// Carrega a blockchain de um arquivo JSON
func (bc *Blockchain) loadFromFile() error {
	data, err := os.ReadFile(bc.dbPath)
	if err != nil {
		return err
	}

	return json.Unmarshal(data, &bc.Chain)
}

func main() {
	// Configurar diretório de dados
	dataDir := "./data"
	if _, err := os.Stat(dataDir); os.IsNotExist(err) {
		os.MkdirAll(dataDir, 0755)
	}

	// Inicializar blockchain
	blockchain := NewBlockchain(dataDir + "/blockchain.json")

	// Inicializar servidor Gin
	router := gin.Default()

	// Configurar CORS
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "ok",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	})

	// Obter toda a blockchain
	router.GET("/chain", func(c *gin.Context) {
		c.JSON(http.StatusOK, blockchain.Chain)
	})

	// Minerar um novo bloco
	router.POST("/mine", func(c *gin.Context) {
		var req MineRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		newBlock := blockchain.addBlock(req.Data)

		response := MineResponse{
			Message: "Novo bloco adicionado à blockchain",
			Index:   newBlock.Index,
			Hash:    newBlock.Hash,
		}

		c.JSON(http.StatusOK, response)
	})

	// Validar a blockchain
	router.GET("/validate", func(c *gin.Context) {
		isValid := blockchain.isValid()
		c.JSON(http.StatusOK, ValidateResponse{Valid: isValid})
	})

	// Obter um bloco específico pelo hash
	router.GET("/blocks/:hash", func(c *gin.Context) {
		hash := c.Param("hash")
		block, found := blockchain.getBlockByHash(hash)
		if !found {
			c.JSON(http.StatusNotFound, gin.H{"error": "Bloco não encontrado"})
			return
		}
		c.JSON(http.StatusOK, block)
	})

	// Buscar bloco por detection_id
	router.GET("/search", func(c *gin.Context) {
		detectionID := c.Query("detection_id")
		if detectionID == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "detection_id é obrigatório"})
			return
		}

		block, found := blockchain.searchBlockByDetectionID(detectionID)
		if !found {
			c.JSON(http.StatusNotFound, gin.H{"error": "Nenhum bloco encontrado com este detection_id"})
			return
		}

		c.JSON(http.StatusOK, block)
	})

	// Determinar porta do servidor
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Iniciar servidor
	log.Printf("Servidor blockchain iniciado na porta %s", port)
	router.Run(":" + port)
}
