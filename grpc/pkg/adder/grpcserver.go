package adder

import (
	"context"
	"grpc_server/pkg/api"
)

type GRPCServer struct {
	api.AdderServer
}

func (s *GRPCServer) Add(ctx context.Context, req *api.AddRequest) (*api.AddResponse, error) {
	return &api.AddResponse{
		Result: req.GetX() + req.GetY(),
	}, nil
}
