package main

import (
	"context"
	"fmt"
	"log"
	stt_handler "wails_client/pkg/stt"
)

// App struct
type App struct {
	sttHandler  *stt_handler.Recognizer
	isConnected bool
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{
		isConnected: true,
	}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	// a.ctx = ctx
	a.sttHandler = stt_handler.NewRecognizer()

	if err := a.sttHandler.NewGRPCConnection(ctx); err != nil {
		log.Fatalf("Can't create gRPC connection: %v", err)
	}

	if err := a.sttHandler.StartStream(); err != nil {
		log.Fatalf("Can't create stream: %v", err)
	}
}

func (a *App) shutdown(ctx context.Context) {
	if err := a.sttHandler.CloseGRPCConnection(); err != nil {
		log.Fatalf("Can't close connection: %v", err)
	}
}

// Greet returns a greeting for the given name
func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}

// Test returns a test strnig
func (a *App) Test(name string) string {
	return fmt.Sprintf("Hello %s, It's test!", name)
}

func (a *App) ProcessAudioBase64(audioBase64 string) error {
	// fmt.Println("UNIMPLEMENTED")

	a.sttHandler.HandleGRPCResponses()

	a.sttHandler.GenerateTestStream()

	return nil
}

// func (a *App) ProcessAudioBase64(audioBase64 string) error {
// 	// Decode base64 string
// 	decoded, err := base64.StdEncoding.DecodeString(audioBase64)
// 	if err != nil {
// 		return err
// 	}

// 	// Construct file path
// 	dir := "audio"
// 	if err := os.MkdirAll(dir, 0755); err != nil {
// 		return err
// 	}
// 	// TODO: filename := fmt.Sprintf("%s/audio%s.ogg", dir, uuid.New())
// 	filename := fmt.Sprintf("%s/audio.webm", dir)

// 	// VAR 1
// 	if err := os.WriteFile(filename, decoded, 0644); err != nil {
// 		log.Fatal(err)
// 		return err
// 	}

// 	// VAR 2
// 	// f, _ := os.Create(filename)

// 	// samples := AddRIFFHeader(decoded, sampleRate, numChannels, bitDepth)

// 	// for _, sample := range samples {
// 	// 	binary.Write(f, binary.LittleEndian, sample)
// 	// }

// 	// // VAR 3
// 	// f, _ := os.Create(filename)
// 	// defer f.Close()

// 	// numChannels := 1
// 	// sampleRate := 8000
// 	// bitDepth := 16

// 	// // Create new WAV encoder
// 	// enc := wav.NewEncoder(f, numChannels, sampleRate, bitDepth, 1)

// 	// // Byte array of raw PCM samples
// 	// ints := make([]int, len(decoded))
// 	// for i, b := range decoded {
// 	// 	ints[i] = int(b)
// 	// }
// 	// buf := &audio.IntBuffer{
// 	// 	Data: ints,
// 	// 	Format: &audio.Format{
// 	// 		NumChannels: numChannels,
// 	// 		SampleRate:  sampleRate,
// 	// 	},
// 	// 	SourceBitDepth: bitDepth,
// 	// }

// 	// // Write bytes directly
// 	// enc.Write(buf)

// 	// // Close encoder
// 	// enc.Close()

// 	return nil
// }
