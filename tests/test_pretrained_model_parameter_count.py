from __future__ import annotations

import unittest

import torch

from utils_zp.pretrained_model_parameter_count import count_model_parameters


class CountModelParametersTests(unittest.TestCase):
    def test_counts_total_parameters_for_torch_module(self) -> None:
        model = torch.nn.Sequential(
            torch.nn.Linear(4, 3),
            torch.nn.Linear(3, 2),
        )

        count = count_model_parameters(model)

        self.assertEqual(count, 23)

    def test_counts_only_trainable_parameters_for_torch_module(self) -> None:
        model = torch.nn.Sequential(
            torch.nn.Linear(4, 3),
            torch.nn.Linear(3, 2),
        )
        model[1].weight.requires_grad = False
        model[1].bias.requires_grad = False

        total_count = count_model_parameters(model)
        trainable_count = count_model_parameters(model, trainable_only=True)

        self.assertEqual(total_count, 23)
        self.assertEqual(trainable_count, 15)


if __name__ == "__main__":
    unittest.main()
