from typing import Any, Literal


class TrainingConfigAdapter:
    
    training_fraction: float
    
    resnet: int

    net_type: Literal["resnet_50", 
                      "resnet_101", 
                      "resnet_152", 
                      "mobilenet_v2_1.0",
                      "mobilenet_v2_0.75",
                      "mobilenet_v2_0.5",
                      "mobilenet_v2_0.35",
                      "efficientnet-b0",
                      "efficientnet-b1",
                      "efficientnet-b2",
                      "efficientnet-b3",
                      "efficientnet-b4",
                      "efficientnet-b5",
                      "efficientnet-b6",]
    
    maxiters: int

    lr_init: float

    def __init__(self, config: dict[Any, Any]):
        self.training_fraction = 1-config["test_fraction"]
        self.maxiters = config["num_epochs"]
        self.net_type = config["backbone_model"]
        self.resnet = config["resnet"]
        self.lr_init = config["learning_rate"]