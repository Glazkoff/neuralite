package stt_handler

import (
	"context"
	"encoding/binary"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/mjibson/go-dsp/wav"
	"github.com/wailsapp/wails/v2/pkg/runtime"
	"github.com/yandex-cloud/go-genproto/yandex/cloud/ai/stt/v3"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/metadata"
)

type Recognizer struct {
	connectionCtx  context.Context
	grpcConnection *grpc.ClientConn
	CurrentStream  stt.Recognizer_RecognizeStreamingClient
}

func NewRecognizer() *Recognizer {
	return &Recognizer{}
}

func GenerateSettingsRequest(sampleRate int64, channelCount int64) stt.StreamingRequest {
	return stt.StreamingRequest{
		Event: &stt.StreamingRequest_SessionOptions{
			SessionOptions: &stt.StreamingOptions{
				RecognitionModel: &stt.RecognitionModelOptions{
					AudioFormat: &stt.AudioFormatOptions{
						AudioFormat: &stt.AudioFormatOptions_RawAudio{
							RawAudio: &stt.RawAudio{
								AudioEncoding: stt.RawAudio_LINEAR16_PCM,
								// AudioEncoding:     stt.RawAudio_AUDIO_ENCODING_UNSPECIFIED,
								SampleRateHertz:   sampleRate, // для аудио - 44100
								AudioChannelCount: channelCount,
							},
						},
					},
					// AudioFormat: &stt.AudioFormatOptions{
					// 	AudioFormat: &stt.AudioFormatOptions_ContainerAudio{
					// 		ContainerAudio: &stt.ContainerAudio{
					// 			ContainerAudioType: stt.ContainerAudio_WAV,
					// 		},
					// 	},
					// },
					TextNormalization: &stt.TextNormalizationOptions{
						TextNormalization: stt.TextNormalizationOptions_TEXT_NORMALIZATION_ENABLED,
						ProfanityFilter:   true,
						LiteratureText:    false,
					},
					LanguageRestriction: &stt.LanguageRestrictionOptions{
						RestrictionType: stt.LanguageRestrictionOptions_WHITELIST,
						LanguageCode:    []string{"ru-RU"},
					},
					AudioProcessingType: stt.RecognitionModelOptions_REAL_TIME,
				},
			},
		},
	}
}

func (r *Recognizer) NewGRPCConnection(appCtx context.Context) error {
	md := metadata.Pairs("authorization", "Api-Key AQVN11-WpDNZ3kKtcD4bTjHWirG3xuFKaSwFuRkd")
	r.connectionCtx = metadata.NewOutgoingContext(appCtx, md)
	creds := credentials.NewClientTLSFromCert(nil, "")
	grpcConnection, err := grpc.DialContext(r.connectionCtx, "stt.api.cloud.yandex.net:443", grpc.WithTransportCredentials(creds))
	r.grpcConnection = grpcConnection
	return err
}

func (r *Recognizer) CloseGRPCConnection() error {
	return r.grpcConnection.Close()
}

func (r *Recognizer) StartStream(sampleRate int64, channelCount int64) error {
	recognizerClient := stt.NewRecognizerClient(r.grpcConnection)
	stream, err := recognizerClient.RecognizeStreaming(r.connectionCtx)
	if err != nil {
		return err
	}

	// # Задайте настройки распознавания.
	request := GenerateSettingsRequest(sampleRate, channelCount)

	// Отправьте сообщение с настройками распознавания.
	if err := stream.Send(&request); err != nil {
		return err
	}

	r.CurrentStream = stream
	return nil
}

func (r *Recognizer) HandleGRPCResponses() {
	go func() {
		fmt.Println("--- START RECEIVE GRPC RESPONSES ---")
		for {
			response, err := r.CurrentStream.Recv()
			if err != nil {
				log.Fatalf("Error receiving message: %v", err)
				return
			}

			switch response.Event.(type) {
			case *stt.StreamingResponse_Partial:
				var alternatives []*stt.Alternative = response.GetPartial().GetAlternatives()
				var words []*stt.Word
				var text []string
				for _, alternative := range alternatives {
					words = append(words, alternative.GetWords()...)
					text = append(text, alternative.GetText())
				}
				fmt.Println("PARTIAL: ", text)
				runtime.EventsEmit(r.connectionCtx, "get_response", text)
			case *stt.StreamingResponse_Final:
				fmt.Println("FINAL: ", response.GetFinal().GetAlternatives())
			case *stt.StreamingResponse_FinalRefinement:
				fmt.Println("FINAL REFINEMENT: ", response.GetFinalRefinement().GetNormalizedText().GetAlternatives())
			}
		}
	}()
}

func (r *Recognizer) GenerateTestStream() {
	// Отправляем чанки файла
	// file, err := os.Open("../grpc/wails_client/audio/audio.wav")
	file, err := os.Open("D:/Development/neuralite_backend/test/test.wav")
	if err != nil {
		log.Fatalf("Failed to open audio file: %v", err)
	}
	defer file.Close()

	// Decode WAV
	decodedWav, err := wav.New(file)
	if err != nil {
		log.Fatalf("Failed to decode audio file: %v", err)
	}

	fmt.Println(decodedWav.Header)
	fmt.Println("duration(ms):", decodedWav.Duration.Milliseconds())

	chunkDuration := time.Duration(time.Millisecond * 400)
	fmt.Println("chunk duration(ms):", chunkDuration.Milliseconds())

	sampleRate := decodedWav.Header.SampleRate
	fmt.Println("sampleRate(samples/s):", sampleRate)

	chunkSizeSamples := int(float64(sampleRate) * chunkDuration.Seconds())
	fmt.Println("chunkSize(samples/chunk):", float64(sampleRate)*chunkDuration.Seconds(), chunkSizeSamples)

	chunksNum := decodedWav.Duration.Milliseconds() / chunkDuration.Milliseconds()
	if decodedWav.Duration.Milliseconds()%chunkDuration.Milliseconds() != 0 {
		chunksNum++
	}
	fmt.Println("chunks(num):", chunksNum)

	samplesPerChunk := float64(sampleRate) * chunkDuration.Seconds()
	fmt.Println("samples per chunk:", samplesPerChunk)
	fmt.Println("total samples:", decodedWav.Samples)

	allSamples, err := decodedWav.ReadSamples(decodedWav.Samples)
	if err != nil {
		log.Fatalf("Failed to read audio file: %v", err)
	}

	allSamplesInts, ok := allSamples.([]int16)
	if !ok {
		log.Fatalf("error: invalid type assertion")
	}

	allSamplesBytes := make([]byte, len(allSamplesInts)*2)
	for i, v := range allSamplesInts {
		// binary.BigEndian.PutUint16()
		binary.LittleEndian.PutUint16(allSamplesBytes[i*2:], uint16(v))
	}

	fmt.Println("--- START SEND GRPC REQUESTS ---")
	for i := 0; i < int(chunksNum); i++ {

		// fmt.Println(reflect.TypeOf(allSamplesInts))
		startIndex := i * chunkSizeSamples
		endIndex := (i + 1) * chunkSizeSamples

		// chunkInts := allSamplesInts[startIndex:endIndex]
		// fmt.Println(chunkInts[0:10])

		chunkBytes := allSamplesBytes[startIndex:endIndex]
		// fmt.Println(reflect.TypeOf(allSamplesBytes), chunkBytes[0:10])

		// Отправляем чанк
		audioChunk := stt.AudioChunk{
			Data: chunkBytes,
		}
		request := GenerateSettingsRequest(int64(sampleRate), 1)
		request.SetChunk(&audioChunk)
		if err := r.CurrentStream.Send(&request); err != nil {
			log.Fatalf("did not connect 4: %v", err)
		}

		time.Sleep(chunkDuration)
	}

	time.Sleep(time.Duration(time.Second * 20))
	fmt.Println("SUCCESS(?)")
}
