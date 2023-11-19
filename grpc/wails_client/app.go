package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"log"
	"os"
	"time"
	stt_handler "wails_client/pkg/stt"

	wavv "github.com/go-audio/wav"
	goWav "github.com/youpy/go-wav"

	"github.com/yandex-cloud/go-genproto/yandex/cloud/ai/stt/v3"
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
	a.sttHandler = stt_handler.NewRecognizer()

	if err := a.sttHandler.NewGRPCConnection(ctx); err != nil {
		log.Fatalf("Can't create gRPC connection: %v", err)
	}

	// if err := a.sttHandler.StartStream(); err != nil {
	// 	log.Fatalf("Can't create stream: %v", err)
	// }
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

func (a *App) ProcessAudioBase64(audioBase64 string, sampleRate int64, sampleSize int64, channelCount int64, bytesSize int64) error {
	fmt.Println("UNIMPLEMENTED")
	bytesPerSample := sampleSize / 8
	numSamples := bytesSize / bytesPerSample
	duration := float64(numSamples) / float64(sampleRate)
	fmt.Printf("sampleRate: %d\nsampleSize: %d\nchannelCount: %d\nsize: %d\nduration: %.2f\n", sampleRate, sampleSize, channelCount, bytesSize, duration)

	if err := a.sttHandler.StartStream(sampleRate, channelCount); err != nil {
		log.Fatalf("Can't create stream: %v", err)
	}

	a.sttHandler.HandleGRPCResponses()

	decoded, err := base64.StdEncoding.DecodeString(audioBase64)
	if err != nil {
		log.Fatalf("Failed to decode base64: %v", err)
		return err
	}

	f, err := os.CreateTemp("", "decoded")
	if err != nil {
		log.Fatalf("Failed to create temp file: %v", err)
		return err
	}

	if _, err := f.Write(decoded); err != nil {
		log.Fatalf("Failed to write temp file: %v", err)
		return err
	}

	err = os.WriteFile("test_audio.wav", decoded, 0644)
	if err != nil {
		panic(err)
	}

	fWav, err := os.Create("test_form_audio.wav")
	if err != nil {
		log.Fatalf("Failed to create form file: %v", err)
		return err
	}

	// Отправляем чанками
	chunkDuration := time.Duration(time.Millisecond * 200)
	var chunkBytesSize int = 10000
	var chunksNum int = int(bytesSize) / chunkBytesSize
	if int(bytesSize)%chunkBytesSize != 0 {
		chunksNum++
	}

	for i := 0; i < chunksNum; i++ {
		fmt.Println("i: ", i)
		startIndex := i * chunkBytesSize
		endIndex := (i + 1) * chunkBytesSize

		if i == chunksNum-1 {
			endIndex = int(bytesSize) - 1
		}

		chunkBytes := decoded[startIndex:endIndex]
		audioChunk := stt.AudioChunk{
			Data: chunkBytes,
		}
		request := stt_handler.GenerateSettingsRequest(sampleRate, channelCount)
		request.SetChunk(&audioChunk)
		if err := a.sttHandler.CurrentStream.Send(&request); err != nil {
			log.Fatalf("did not connect 4: %v", err)
		}

		time.Sleep(chunkDuration)
	}

	// TODO: записать файл с заголовками
	encoder := wavv.NewEncoder(f, int(sampleRate), int(sampleSize), int(channelCount), 1)
	fmt.Println(encoder.NumChans)

	sampleCount := (bytesSize * 8) / sampleSize
	writer := goWav.NewWriter(fWav, uint32(sampleCount), uint16(channelCount), uint32(sampleRate), uint16(sampleSize))

	var samples []goWav.Sample
	for i := 0; i < len(decoded); i = i + 2 {
		sample := goWav.Sample{Values: [2]int{int(decoded[i])}}
		samples = append(samples, sample)
	}

	writer.WriteSamples()
	// encoder.WriteFrame()

	// audioChunk := stt.AudioChunk{
	// 	Data: decoded,
	// }
	// request := stt_handler.GenerateSettingsRequest(sampleRate, channelCount)
	// request.SetChunk(&audioChunk)
	// if err := a.sttHandler.CurrentStream.Send(&request); err != nil {
	// 	log.Fatalf("did not connect 4: %v", err)
	// }

	// decodedWav, err := wav.New(f)
	// if err != nil {
	// 	log.Fatalf("Failed to decode audio file: %v", err)
	// }
	// fmt.Println(decodedWav.Header)
	// fmt.Println("duration(ms):", decodedWav.Duration.Milliseconds())

	// file, err := os.Open("D:/Development/neuralite_backend/test/test.wav")
	// if err != nil {
	// 	log.Fatalf("Failed to open audio file: %v", err)
	// }
	// defer file.Close()

	// // Decode WAV
	// decodedWav, err := wav.New(file)
	// if err != nil {
	// 	log.Fatalf("Failed to decode audio file: %v", err)
	// }

	// a.sttHandler.GenerateTestStream()

	return nil
}

func (a *App) StopAudioProcessing() error {
	// TODO: fix it
	return a.sttHandler.CloseGRPCConnection()
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
