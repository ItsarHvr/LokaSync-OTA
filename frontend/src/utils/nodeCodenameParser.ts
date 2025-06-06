export interface ParsedNodeCodename {
  node_location: string;
  node_type: string;
  node_id: string;
  full_codename: string;
}

export function parseNodeCodename(
  nodeCodename: string,
): ParsedNodeCodename | null {
  // Expected format: "location_type_id" (e.g., "cibubur-sayuranpagi_pembibitan_1a")
  const parts = nodeCodename.split("_");

  if (parts.length >= 3) {
    const location = parts[0];
    const type = parts[1];
    const id = parts.slice(2).join("_"); // In case ID contains underscores

    return {
      node_location: location,
      node_type: type,
      node_id: id,
      full_codename: nodeCodename,
    };
  }

  return null;
}

export function getNodeDisplayName(parsedNode: ParsedNodeCodename): string {
  return `${parsedNode.node_location} - ${parsedNode.node_type} (${parsedNode.node_id})`;
}
