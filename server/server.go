package main

import (
	"container/list"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"log/slog"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	pb "grpc/grpc_instagram_server"

	"github.com/ggerganov/whisper.cpp/bindings/go/pkg/whisper"
	"github.com/go-audio/wav"
	"github.com/google/uuid"
	"github.com/gorilla/mux"
	"github.com/lrstanley/go-ytdlp"
	"github.com/tmc/langchaingo/llms"
	"github.com/tmc/langchaingo/llms/ollama"
	ffmpeg "github.com/u2takey/ffmpeg-go"
	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type Video struct {
	ID           bson.ObjectID `bson:"_id"`
	Url          string        `bson:"URL"`
	Channel      int64         `bson:"channel"`
	File         string        `bson:"file"`
	Instructions string        `bson:"instructions"`
	Message      string        `bson:"message"`
	Server       int64         `bson:"server"`
	State        string        `bson:"state"`
	Summarize    bool          `bson:"summarize"`
	UserId       int64         `bson:"user_id"`
	Summary      string
}

type ytdlpVideoInfo struct {
	Executable string   `json:"executable"`
	Args       []string `json:"args"`
	ExitCode   int      `json:"exit_code"`
	Stdout     string   `json:"stdout"`
	Stderr     string   `json:"stderr"`
	OutputLogs []struct {
		Timestamp string `json:"timestamp"`
		Line      string `json:"line"`
		JSON      struct {
			ID      string `json:"id"`
			Title   string `json:"title"`
			Formats []struct {
				FormatID   string  `json:"format_id"`
				FormatNote string  `json:"format_note,omitempty"`
				Ext        string  `json:"ext"`
				Protocol   string  `json:"protocol"`
				Acodec     string  `json:"acodec,omitempty"`
				Vcodec     string  `json:"vcodec"`
				URL        string  `json:"url"`
				Width      int     `json:"width,omitempty"`
				Height     int     `json:"height,omitempty"`
				Fps        float64 `json:"fps,omitempty"`
				Rows       int     `json:"rows,omitempty"`
				Columns    int     `json:"columns,omitempty"`
				Fragments  []struct {
					URL      string  `json:"url"`
					Duration float64 `json:"duration"`
				} `json:"fragments,omitempty"`
				AudioExt       string  `json:"audio_ext"`
				VideoExt       string  `json:"video_ext"`
				Vbr            int     `json:"vbr"`
				Abr            int     `json:"abr"`
				Tbr            any     `json:"tbr"`
				Resolution     string  `json:"resolution"`
				AspectRatio    float64 `json:"aspect_ratio"`
				FilesizeApprox any     `json:"filesize_approx,omitempty"`
				HTTPHeaders    struct {
					UserAgent      string `json:"User-Agent"`
					Accept         string `json:"Accept"`
					AcceptLanguage string `json:"Accept-Language"`
					SecFetchMode   string `json:"Sec-Fetch-Mode"`
				} `json:"http_headers"`
				Format             string `json:"format"`
				FormatIndex        any    `json:"format_index,omitempty"`
				ManifestURL        string `json:"manifest_url,omitempty"`
				Language           string `json:"language,omitempty"`
				Preference         any    `json:"preference,omitempty"`
				Quality            int    `json:"quality,omitempty"`
				HasDrm             bool   `json:"has_drm,omitempty"`
				SourcePreference   int    `json:"source_preference,omitempty"`
				NeedsTesting       bool   `json:"__needs_testing,omitempty"`
				AvailableAt        int    `json:"available_at,omitempty"`
				Asr                int    `json:"asr,omitempty"`
				Filesize           int    `json:"filesize,omitempty"`
				AudioChannels      int    `json:"audio_channels,omitempty"`
				LanguagePreference int    `json:"language_preference,omitempty"`
				DynamicRange       any    `json:"dynamic_range,omitempty"`
				Container          string `json:"container,omitempty"`
				DownloaderOptions  struct {
					HTTPChunkSize int `json:"http_chunk_size"`
				} `json:"downloader_options,omitempty"`
				Working bool `json:"__working,omitempty"`
			} `json:"formats"`
			Thumbnails []struct {
				URL        string `json:"url"`
				Preference int    `json:"preference"`
				ID         string `json:"id"`
				Height     int    `json:"height,omitempty"`
				Width      int    `json:"width,omitempty"`
				Resolution string `json:"resolution,omitempty"`
			} `json:"thumbnails"`
			Thumbnail        string   `json:"thumbnail"`
			Description      string   `json:"description"`
			ChannelID        string   `json:"channel_id"`
			ChannelURL       string   `json:"channel_url"`
			Duration         int      `json:"duration"`
			ViewCount        int      `json:"view_count"`
			AverageRating    any      `json:"average_rating"`
			AgeLimit         int      `json:"age_limit"`
			WebpageURL       string   `json:"webpage_url"`
			Categories       []string `json:"categories"`
			Tags             []string `json:"tags"`
			PlayableInEmbed  bool     `json:"playable_in_embed"`
			LiveStatus       string   `json:"live_status"`
			MediaType        string   `json:"media_type"`
			ReleaseTimestamp any      `json:"release_timestamp"`
			FormatSortFields []string `json:"_format_sort_fields"`
			Subtitles        struct {
			} `json:"subtitles"`
			CommentCount int `json:"comment_count"`
			Chapters     any `json:"chapters"`
			Heatmap      []struct {
				StartTime float64 `json:"start_time"`
				EndTime   float64 `json:"end_time"`
				Value     float64 `json:"value"`
			} `json:"heatmap"`
			LikeCount            int    `json:"like_count"`
			Channel              string `json:"channel"`
			ChannelFollowerCount int    `json:"channel_follower_count"`
			Uploader             string `json:"uploader"`
			UploaderID           string `json:"uploader_id"`
			UploaderURL          string `json:"uploader_url"`
			UploadDate           string `json:"upload_date"`
			Timestamp            int    `json:"timestamp"`
			Availability         string `json:"availability"`
			OriginalURL          string `json:"original_url"`
			WebpageURLBasename   string `json:"webpage_url_basename"`
			WebpageURLDomain     string `json:"webpage_url_domain"`
			Extractor            string `json:"extractor"`
			ExtractorKey         string `json:"extractor_key"`
			Playlist             any    `json:"playlist"`
			PlaylistIndex        any    `json:"playlist_index"`
			DisplayID            string `json:"display_id"`
			Fulltitle            string `json:"fulltitle"`
			DurationString       string `json:"duration_string"`
			ReleaseYear          any    `json:"release_year"`
			IsLive               bool   `json:"is_live"`
			WasLive              bool   `json:"was_live"`
			RequestedSubtitles   any    `json:"requested_subtitles"`
			HasDrm               any    `json:"_has_drm"`
			Epoch                int    `json:"epoch"`
			RequestedFormats     []struct {
				FormatID         string  `json:"format_id"`
				FormatIndex      any     `json:"format_index,omitempty"`
				URL              string  `json:"url"`
				ManifestURL      string  `json:"manifest_url,omitempty"`
				Tbr              float64 `json:"tbr"`
				Ext              string  `json:"ext"`
				Fps              float64 `json:"fps"`
				Protocol         string  `json:"protocol"`
				Preference       any     `json:"preference"`
				Quality          int     `json:"quality"`
				HasDrm           bool    `json:"has_drm"`
				Width            int     `json:"width"`
				Height           int     `json:"height"`
				Vcodec           string  `json:"vcodec"`
				Acodec           string  `json:"acodec"`
				DynamicRange     string  `json:"dynamic_range"`
				SourcePreference int     `json:"source_preference"`
				FormatNote       string  `json:"format_note"`
				AvailableAt      int     `json:"available_at"`
				VideoExt         string  `json:"video_ext"`
				AudioExt         string  `json:"audio_ext"`
				Abr              int     `json:"abr"`
				Vbr              float64 `json:"vbr"`
				Resolution       string  `json:"resolution"`
				AspectRatio      float64 `json:"aspect_ratio"`
				HTTPHeaders      struct {
					UserAgent      string `json:"User-Agent"`
					Accept         string `json:"Accept"`
					AcceptLanguage string `json:"Accept-Language"`
					SecFetchMode   string `json:"Sec-Fetch-Mode"`
				} `json:"http_headers"`
				Format             string `json:"format"`
				Working            bool   `json:"__working,omitempty"`
				Asr                int    `json:"asr,omitempty"`
				Filesize           int    `json:"filesize,omitempty"`
				AudioChannels      int    `json:"audio_channels,omitempty"`
				FilesizeApprox     int    `json:"filesize_approx,omitempty"`
				Language           string `json:"language,omitempty"`
				LanguagePreference int    `json:"language_preference,omitempty"`
				Container          string `json:"container,omitempty"`
				DownloaderOptions  struct {
					HTTPChunkSize int `json:"http_chunk_size"`
				} `json:"downloader_options,omitempty"`
			} `json:"requested_formats"`
			Format         string  `json:"format"`
			FormatID       string  `json:"format_id"`
			Ext            string  `json:"ext"`
			Protocol       string  `json:"protocol"`
			Language       string  `json:"language"`
			FormatNote     string  `json:"format_note"`
			FilesizeApprox int     `json:"filesize_approx"`
			Tbr            float64 `json:"tbr"`
			Width          int     `json:"width"`
			Height         int     `json:"height"`
			Resolution     string  `json:"resolution"`
			Fps            float64 `json:"fps"`
			DynamicRange   string  `json:"dynamic_range"`
			Vcodec         string  `json:"vcodec"`
			Vbr            float64 `json:"vbr"`
			StretchedRatio any     `json:"stretched_ratio"`
			AspectRatio    float64 `json:"aspect_ratio"`
			Acodec         string  `json:"acodec"`
			Abr            float64 `json:"abr"`
			Asr            int     `json:"asr"`
			AudioChannels  int     `json:"audio_channels"`
			Filename       string  `json:"_filename"`
			Filename0      string  `json:"filename"`
			Type           string  `json:"_type"`
			Version        struct {
				Version        string `json:"version"`
				CurrentGitHead any    `json:"current_git_head"`
				ReleaseGitHead string `json:"release_git_head"`
				Repository     string `json:"repository"`
			} `json:"_version"`
		} `json:"json"`
		Pipe string `json:"pipe"`
	} `json:"output_logs"`
}

type probeFormat struct {
	Duration string `json:"duration"`
}

type probeStream struct {
	Codec_Type string `json:"codec_type"`
	Bit_Rate   string `json:"bit_rate"`
}

type probeData struct {
	Format probeFormat   `json:"format"`
	Stream []probeStream `json:"streams"`
}

var q *list.List = list.New()
var VideoJobRunning bool = false
var discordclient DiscordClient

func main() {
	router := mux.NewRouter()
	discordclient = DiscordClient{host: "127.0.0.1", standard_port: 8765, id: uuid.New().String(), secret_key: "theholygrail"}

	router.HandleFunc("/downloadvideos/{guild_id}", startDownloadVideos).Methods("GET")
	slog.Info("Starting http server")
	log.Fatal(http.ListenAndServe(":5102", router))

}

func startDownloadVideos(w http.ResponseWriter, r *http.Request) {
	slog.Info("Request recieved.")
	params := mux.Vars(r)

	guild_id, err := strconv.Atoi(params["guild_id"])

	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	q.PushBack(guild_id)
	if !VideoJobRunning {
		go executeJobs()
	}
}

func executeJobs() {
	VideoJobRunning = true
	for guild := q.Front(); guild != nil; {
		next := guild.Next()
		downloadVideos(guild.Value.(int))
		q.Remove(guild)
		guild = next
	}
	if q.Len() > 0 {
		executeJobs()
	}
	VideoJobRunning = false
}

func downloadVideos(guild_id int) {
	client, err := mongo.Connect(options.Client().ApplyURI("mongodb://192.168.1.107:27017"))
	ctx := context.Background()
	defer func() {
		if err = client.Disconnect(ctx); err != nil {
			panic(err)
		}
	}()
	coll := client.Database("Monty").Collection("downloader")
	var result Video
	filter := bson.D{{"server", guild_id}, {"state", "new"}}
	err = coll.FindOne(context.TODO(), filter).
		Decode(&result)
	if err == mongo.ErrNoDocuments {
		log.Printf("No document was found with the server %d", guild_id)
		return
	}
	slog.Info("Results were found with the server %d", guild_id)
	jsonData, err := json.MarshalIndent(result, "", "    ")
	slog.Info(result.Url)
	slog.Info("\n", jsonData)
	filter = bson.D{{"_id", result.ID}}
	updateJobState(coll, filter, "Started")
	finished, msg := downloadVideo(&result, coll, filter)
	if !finished {
		//fail this job for msg
		log.Println(msg)
		failJobState(coll, filter, msg)
	}
	discordclient.Post_Ipc("post_jobs")
}

func summarizeVideo(File string, DownloadPath string, result *Video) {
	// get multiple output with different size/bitrate
	SDFile := "sd_" + File
	ffmpeg.Input(filepath.Join(DownloadPath, File)).Filter("scale", ffmpeg.Args{"640:-1"}).
		Output(filepath.Join(DownloadPath, SDFile), ffmpeg.KwArgs{"b:v": "2800k"}).Run()
	//Down sample to 16 kHz for whisper.cpp
	ffmpeg.Input(filepath.Join(DownloadPath, File)).Output(filepath.Join(DownloadPath, "audio.wav"), ffmpeg.KwArgs{"c:a": "pcm_s16le", "map": "0:a:0", "ar": 16000, "ac": 1}).Run()
	os.Mkdir(filepath.Join(DownloadPath, "frames"), 0755)
	ffmpeg.Input(filepath.Join(DownloadPath, SDFile)).
		Output(filepath.Join(DownloadPath, "frames/frame%d.jpg"), ffmpeg.KwArgs{"q:v": "2"}).
		Run()
	os.Remove(filepath.Join(DownloadPath, SDFile))
	//Figure out whisper go bindings
	modelPath := "/src/bot/models/ggml-base.bin"
	model, err := whisper.New(modelPath)
	if err != nil {
		fmt.Printf("Error loading model: %v\n", err)
		os.Exit(1)
	}
	defer model.Close() // Ensure the model is closed when done
	// Create a new transcription context

	Wcontext, err := model.NewContext()
	Wcontext.SetEntropyThold(2.5)
	Wcontext.SetThreads(2)
	Wcontext.SetLanguage("en")
	Wcontext.SetTranslate(false)

	f, err := os.Open(filepath.Join(DownloadPath, "audio.wav"))
	if err != nil {
		fmt.Printf("Error opening file: %v\n", err)
		return
	}
	defer f.Close()

	// Decode the WAV file - load the full buffer
	dec := wav.NewDecoder(f)
	buf, err := dec.FullPCMBuffer()
	if err != nil {
		log.Fatalf("Oh no!", err)
	} else if dec.SampleRate != whisper.SampleRate {
		log.Fatalf("unsupported sample rate: %d", dec.SampleRate)
	} else if dec.NumChans != 1 {
		log.Fatalf("unsupported number of channels: %d", dec.NumChans)
	}
	samples := buf.AsFloat32Buffer().Data

	// Process the audio samples for transcription
	if err := Wcontext.Process(samples, nil, nil, nil); err != nil {
		fmt.Printf("Error processing samples: %v\n", err)
		os.Exit(1)
	}
	// Iterate through the transcribed segments and print them
	transcript := ""
	for {
		segment, err := Wcontext.NextSegment()
		if err != nil {
			// No more segments or an error occurred
			break
		}
		transcript += fmt.Sprintf("[%6s->%6s] %s\n", segment.Start, segment.End, segment.Text)
		fmt.Printf("[%6s->%6s] %s\n", segment.Start, segment.End, segment.Text)
	}

	log.Println(transcript)
	os.Remove(filepath.Join(DownloadPath, "audio.wav"))

	System := `
- You are a Discord-focused video summarization AI. Your primary task is to generate concise, informative summaries
of video content, tailored for quick consumption within a Discord channel. 
- You will receive a list of key frames and a transcript of the audio.
- Your summaries MUST be less than 2000 characters (approximately 75-150 words) and are intended to be easily digestible within a Discord message.
`
	User := `**Here's how you will operate:**

1. **Input:** You will receive two pieces of information:
   * **Frames:** A list of key frames extracted from the video.
   * **Transcript:** A full transcript of the audio track from the video.

2. **Processing & Summary Generation (Constraints):**
   * **Length Limit:** Your summary MUST be less than 2000 characters. Prioritize clarity and conciseness.
   * **Format:** Create a short, 3-sentence summary. Each sentence should capture a key aspect of the video.
   * **Content Focus:**  The summary should accurately reflect the main points.  Avoid tangential details or
embellishments.
   * **Discord Optimization:** The language should be straightforward and suitable for quick understanding within
a Discord chat.

3. **Output:** Provide your summary as follows:

   **Summary:** [Your concise summary here - under 2000 characters]

 ---

**Example Input:**

**Frames:** [Imagine a list of frames showing: 1. A person speaking at a podium. 2. Close-up of the speaker's
hands gesturing. 3.  A graph displaying rising sales figures.]

**Transcript:** 
[  4.6s-> 5.76s] "Good morning, everyone. Today, I'm thrilled to share some
[ 5.76s-> 7.96s] fantastic news. Our Q3 sales figures have exceeded all expectations, jumping by 15% thanks to our innovative marketing campaign. This growth is a
[ 7.96s-> 9.08s] direct result of the team’s hard work and dedication. We'll now delve into the specifics…" 


---

**Expected Output (Example -  will vary based on the provided frames/transcript):**

**Summary:** "This video reports on exceptionally strong Q3 sales growth, hitting a remarkable 15% increase. The
success is attributed to a successful marketing campaign and the dedication of the team.  The video provides a
positive update on the company's performance."  (Approximately 130 characters)

**Important Notes for Your AI Model:**

*   **Contextual Awareness:** Prioritize understanding the connections between the images and the spoken words.
*   **Conciseness is Key:**  Remember, this is for Discord!
*   **Error Handling:** If the input is unclear, politely request clarification.  Don't fabricate information.
 
   `

	/*System := "You are an expert at writing summaries for videos." +
	" Using only the provided transcript of the audio and the frames of a video," +
	" summarize this video in a few sentences." +
	" Be brief in the summary and remain unbias." + " Your response should be less than 2000 characters." +
	" Shorten your output if you are more than 2000 characters."
	*/
	log.Println("Starting LLM connection")

	llm, err := ollama.New(ollama.WithModel("gemma3"))
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()

	entries, err := os.ReadDir(filepath.Join(DownloadPath, "frames"))
	if err != nil {
		log.Fatalf("failed to read directory: %w", err)
	}
	Parts := []llms.ContentPart{}

	for _, entry := range entries {
		if !entry.IsDir() {
			imgData, err := os.ReadFile(filepath.Join(DownloadPath, "frames", entry.Name()))
			if err != nil {
				log.Fatalf("Failed to read file %w", err)
			}
			Parts = append(Parts, llms.BinaryPart("image/jpeg", imgData))
		}
	}
	log.Println("Images loaded")

	if result.Instructions != "" {
		Parts = append(Parts, llms.TextPart(result.Instructions))
	}

	messages := []llms.MessageContent{
		{
			Role: llms.ChatMessageTypeSystem,
			Parts: []llms.ContentPart{
				llms.TextPart(System),
			},
		},
		{
			Role: llms.ChatMessageTypeHuman,
			Parts: []llms.ContentPart{
				llms.TextPart(User),
			},
		},
		{
			Role: llms.ChatMessageTypeHuman,
			Parts: []llms.ContentPart{
				llms.TextPart("Give me a brief summary of this video and transcript." +
					" Only give me a few setences. Do NOT make the summary too long. DO NOT REPEAT THE TRANSCRIPT"),
			},
		},
		{
			Role:  llms.ChatMessageTypeHuman,
			Parts: Parts,
		},
		{
			Role: llms.ChatMessageTypeHuman,
			Parts: []llms.ContentPart{
				llms.TextPart(transcript),
			},
		},
	}
	log.Println("LLM started")

	resp, err := llm.GenerateContent(
		ctx,
		messages,
		llms.WithTemperature(0.1),
	)
	if err != nil {
		log.Fatal(err)
	}
	choices := resp.Choices
	if len(choices) < 1 {
		log.Fatal("empty response from model")
	}
	result.Summary = choices[0].Content
	log.Println(choices[0].Content)
	err = os.RemoveAll(filepath.Join(DownloadPath, "frames"))
	if err != nil {
		log.Fatalf("Error removing directory: %v", err)
	}

}
func updateJobState(coll *mongo.Collection, filter bson.D, state string) {
	update := bson.D{{"$set", bson.D{{"state", state}}}}
	_, err := coll.UpdateOne(context.TODO(), filter, update)
	if err != nil {
		panic(err)
	}
	return
}

func failJobState(coll *mongo.Collection, filter bson.D, reason string) {
	update := bson.D{{"$set", bson.D{{"state", "Failed"}, {"reason", reason}}}}
	_, err := coll.UpdateOne(context.TODO(), filter, update)
	if err != nil {
		panic(err)
	}
	return
}
func downloadVideo(result *Video, coll *mongo.Collection, filter bson.D) (bool, string) {
	ytdlp.MustInstallAll(context.TODO())
	updateJobState(coll, filter, "Download Started")

	basePath := "/src/bot/down"

	_, err := os.Stat(basePath)

	if os.IsNotExist(err) {
		os.Mkdir(basePath, 0755)
	}
	mongoID := result.ID.Hex()
	downloadPath := filepath.Join(basePath, mongoID)

	_, err = os.Stat(downloadPath)

	if os.IsNotExist(err) {
		os.Mkdir(downloadPath, 0755)
	}
	update := bson.D{{"$set", bson.D{{"path", downloadPath}}}}
	_, err = coll.UpdateOne(context.TODO(), filter, update)
	if err != nil {
		panic(err)
	}
	var File string = ""
	var mins uint8 = 0
	if strings.Contains(strings.ToLower(result.Url), "instagram.com") {
		state := "Instaqueue"
		update := bson.D{{"$set", bson.D{{"state", state}}}}
		_, err = coll.UpdateOne(context.TODO(), filter, update)
		//trigger grpc for download
		conn, err := grpc.Dial("localhost:5103", grpc.WithInsecure())
		if err != nil {
			log.Fatalf("did not connect: %v", err)
		}
		defer conn.Close()

		client := pb.NewDownloadInstagramPostClient(conn)

		log.Println("Starting download")
		req := &pb.InstagramRequest{Url: result.Url, Guild: result.Server, State: state}
		r, err := client.Download(context.Background(), req)
		if err != nil {
			if status.Code(err) != codes.InvalidArgument {
				log.Printf("Received unexpected error: %v", err)
			}
			log.Printf("Received error: %v\n %s", err, status.Code(err))

		}
		log.Printf("Greeting: %b", r.GetSuccess())
		if !r.GetSuccess() {
			update = bson.D{{"$set", bson.D{{"state", "new"}}}}
			_, err = coll.UpdateOne(context.TODO(), filter, update)
			return false, "Failed to connect to python"
		}

	} else {
		dl := ytdlp.New().
			PrintJSON().
			FormatSort("res,ext:mp4:m4a")

		r, err := dl.Run(context.TODO(), result.Url)
		if err != nil {
			//video failed to get info. Retry
			log.Printf("%s", err)
			return false, fmt.Sprintf("%s", err)
		}

		var info ytdlpVideoInfo
		jsonData, err := json.Marshal(r)

		err = json.Unmarshal(jsonData, &info)
		times := strings.Split(info.OutputLogs[0].JSON.DurationString, ":")
		timeLength := len(times)
		if timeLength > 2 {
			//Fail this job
			return false, "Video is too long"
		}
		var mins int
		if timeLength < 2 {
			mins = 0
		} else {
			mins, _ = strconv.Atoi(times[0])
		}

		if mins > 20 {
			slog.Error("Video exceeds 20 mins. Failing this job.")
			return false, "Video exceeds 20 mins."
		}

		ytFilePath := filepath.Join(downloadPath, "%(id)s.%(ext)s")
		//Find the length of OutputLogs and take the last one for data.
		File = info.OutputLogs[len(info.OutputLogs)-1].JSON.ID + ".mp4"
		log.Printf("File name: %s", File)
		dl = ytdlp.New().
			PrintJSON().
			NoProgress().
			//AudioMultistreams().
			Format("bv*[ext=mp4]+ba/b[ext=mp4] / bv*+ba/b").
			FormatSort("proto,ext:mp4:m4a,res,br").
			RecodeVideo("mp4").
			NoPlaylist().
			NoOverwrites().
			Continue().
			ProgressFunc(100*time.Millisecond, func(prog ytdlp.ProgressUpdate) {
				fmt.Printf( //nolint:forbidigo
					"%s @ %s [eta: %s] :: %s\n",
					prog.Status,
					prog.PercentString(),
					prog.ETA(),
					prog.Filename,
				)
			}).
			Output(ytFilePath)

		r, err = dl.Run(context.TODO(), result.Url)
		if err != nil {
			panic(err)
		}
	}
	updateJobState(coll, filter, "Downloaded")
	log.Printf("Summarize : %t and mins %d", result.Summarize, mins)
	if result.Summarize && mins < 4 {
		entries, err := os.ReadDir(downloadPath)
		if err != nil {
			log.Fatalf("failed to read directory: %w", err)
		}
		if File == "" {
			File = entries[0].Name()
		}
		updateJobState(coll, filter, "Sumarizing")
		summarizeVideo(File, downloadPath, result)
	}
	fileInfo, err := os.Stat(filepath.Join(downloadPath, File))
	if err != nil {
		if os.IsNotExist(err) {
			log.Fatalf("File '%s' does not exist.\n", filepath.Join(downloadPath, File))
		} else {
			log.Fatalf("Error getting file info: %v\n", err)
		}
	}
	if (fileInfo.Size() / (1024 * 1024)) > 8 {
		// check for compression.
		updateJobState(coll, filter, "Compressing")
		entries, err := os.ReadDir(downloadPath)
		if err != nil {
			log.Fatalf("failed to read directory: %w", err)
		}
		log.Printf("files : %v", entries)

		compress_video_file(filepath.Join(downloadPath, File), filepath.Join(downloadPath, "compressed_"+File), 7800)
		entries, err = os.ReadDir(downloadPath)
		if err != nil {
			log.Fatalf("failed to read directory: %w", err)
		}
		log.Printf("files : %v", entries)

	}
	entries, err := os.ReadDir(downloadPath)
	if err != nil {
		log.Fatalf("failed to read directory: %w", err)
	}
	var files []string

	for _, entry := range entries {
		files = append(files, entry.Name())
	}
	log.Printf("files : %v", entries)

	update = bson.D{{"$set", bson.D{{"state", "Ready!"}, {"path", downloadPath}, {"file", files}, {"summary", result.Summary}}}}
	_, err = coll.UpdateOne(context.TODO(), filter, update)
	if err != nil {
		panic(err)
	}

	log.Println("video downloaded")
	return true, ""
}

func compress_video_file(video_path string, output_path string, target_size int) {
	//Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
	slog.Info("video: %s \n compressed file: %s", video_path, output_path)
	min_audio_bitrate := 32000
	max_audio_bitrate := 256000

	probe, err := ffmpeg.Probe(video_path, ffmpeg.KwArgs{})
	if err != nil {
		log.Fatalf("Error using ffmpeg %w", err)
	}
	pd := probeData{}
	err = json.Unmarshal([]byte(probe), &pd)
	if err != nil {
		log.Fatalf("Error using ffmpeg %w", err)
	}

	audio_bitrate := 0

	bit_rates := []int{}
	for _, stream := range pd.Stream {
		if stream.Codec_Type == "audio" {
			audio_bitrate, err = strconv.Atoi(stream.Bit_Rate)
			bit_rates = append(bit_rates, audio_bitrate)
		}
	}
	audio_bitrate = bit_rates[0]
	duration, err := strconv.ParseFloat(pd.Format.Duration, 64)
	target_total_bitrate := float64(target_size*1024*8) / (1.073741824 * duration)

	if 10*audio_bitrate > int(target_total_bitrate) {
		audio_bitrate = int(target_total_bitrate) / 10
		if audio_bitrate < min_audio_bitrate && min_audio_bitrate < int(target_total_bitrate) {
			audio_bitrate = min_audio_bitrate
		} else if audio_bitrate > max_audio_bitrate {
			audio_bitrate = max_audio_bitrate
		}
	}
	video_bitrate := target_total_bitrate - float64(audio_bitrate)

	//https://trac.ffmpeg.org/wiki/Encode/H.264#twopass
	ffmpeg.Input(video_path).Output(os.DevNull, ffmpeg.KwArgs{"c:v": "libx264", "b:v": video_bitrate, "pass": "1", "f": "mp4"}).OverWriteOutput().Run()
	ffmpeg.Input(video_path).Output(output_path, ffmpeg.KwArgs{"c:v": "libx264", "b:v": video_bitrate, "pass": "2", "c:a": "aac", "b:a": audio_bitrate}).OverWriteOutput().Run()

	os.Remove(video_path)
}
