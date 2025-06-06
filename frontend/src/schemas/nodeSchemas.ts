import { z } from "zod";

export const addNodeSchema = z.object({
  description: z.string().optional(),
  node_id: z
    .string()
    .min(1, "Node ID is required")
    .max(10, "Node ID must be 10 characters or less")
    .regex(/^[a-zA-Z0-9]+$/, "Node ID can only contain letters and numbers"),
  node_location: z
    .string()
    .min(3, "Node location is required")
    .max(255, "Node location must be 255 characters or less"),
  node_type: z
    .string()
    .min(3, "Node type is required")
    .max(255, "Node type must be 255 characters or less"),
});

export const addFirmwareSchema = z.object({
  firmware_version: z
    .string()
    .min(1, "Firmware version is required")
    .max(50, "Firmware version must be less than 50 characters"),
  firmware_url: z
    .string()
    .url("Must be a valid URL")
    .optional()
    .or(z.literal("")),
});

export const editFirmwareSchema = z.object({
  description: z
    .string()
    .max(255, "Description must be 255 characters or less")
    .optional(),
});

export type AddNodeInput = z.infer<typeof addNodeSchema>;
export type AddFirmwareInput = z.infer<typeof addFirmwareSchema>;
export type EditFirmwareInput = z.infer<typeof editFirmwareSchema>;
