package main

import (
	"fmt"

	"github.com/JesusIslam/tldr"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"
)

func main() {
	app := fiber.New()

	app.Use(logger.New())

	app.Post("/summarize", func(c *fiber.Ctx) error {
		type Request struct {
			Text string `json:"text"`
		}

		var req Request

		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid request format",
			})
		}

		bag := tldr.New()
		intoSentences := 1
		result, _ := bag.Summarize(req.Text, intoSentences)

		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"summary": result,
		})
	})

	err := app.Listen(":3000")
	if err != nil {
		fmt.Println("Failed to start server")
	}
}
