import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import Layout from "../../components/layout/Layout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Select from "../../components/ui/Select";
import Pagination from "../../components/ui/Pagination";
import Alert from "../../components/ui/Alert";
import { FirmwareController } from "../../controllers/FirmwareController";
import { fetchWithAuth } from "../../utils/api";
import type { Firmware } from "../../types";

// Interface for firmware version options
interface FirmwareVersionsMap {
  [nodeName: string]: {
    versions: string[];
    loading: boolean;
    error: string;
    urls: Record<string, string>; // Map version to URL
  };
}

// Interface for tracking description edit state
interface EditingState {
  isEditing: boolean;
  nodeName: string | null;
  description: string;
}

const Dashboard = () => {
  // State for firmware data
  const [firmwares, setFirmwares] = useState<Firmware[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize] = useState(10);
  const [totalData, setTotalData] = useState(0);
  
  // New state to store firmware versions for each node
  const [firmwareVersions, setFirmwareVersions] = useState<FirmwareVersionsMap>({});
  
  // State for description editing
  const [editingDescription, setEditingDescription] = useState<EditingState>({
    isEditing: false,
    nodeName: null,
    description: "",
  });
  
  // Ref for the textarea
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // State for filters
  const [filterOptions, setFilterOptions] = useState<{
    nodeId: number[];
    nodeLocation: string[];
    sensorType: string[];
  }>({
    nodeId: [],
    nodeLocation: [],
    sensorType: [],
  });

  // Active filters
  const [selectedNodeId, setSelectedNodeId] = useState<number | undefined>(
    undefined,
  );
  const [selectedLocation, setSelectedLocation] = useState<string | undefined>(
    undefined,
  );
  const [selectedSensorType, setSelectedSensorType] = useState<
    string | undefined
  >(undefined);

  // Effect to focus textarea when editing starts
  useEffect(() => {
    if (editingDescription.isEditing && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [editingDescription.isEditing]);

  // Fetch firmware versions for a specific node
  const fetchFirmwareVersions = async (nodeName: string) => {
    // Skip if we already have loaded versions for this node
    if (firmwareVersions[nodeName] && firmwareVersions[nodeName].versions.length > 0) {
      return;
    }

    // Initialize or update loading state
    setFirmwareVersions(prev => ({
      ...prev,
      [nodeName]: {
        ...prev[nodeName] || {},
        loading: true,
        error: '',
        versions: [],
        urls: {},
      }
    }));

    try {
      // Fetch versions from the backend
      interface FirmwareItem {
        firmware_version: string;
        firmware_url: string;
      }
      
      interface FirmwareResponse {
        firmware_data: FirmwareItem[];
      }
      
      const response = await fetchWithAuth<FirmwareResponse>(`/firmware/get_by_node_name/${nodeName}?page=1&page_size=10`);
      
      // Extract versions from response with proper typing
      const versions: string[] = response.firmware_data.map(
        (item: FirmwareItem) => item.firmware_version
      );
      
      // Create a map of version to URL
      const urlMap: Record<string, string> = {};
      response.firmware_data.forEach((item: FirmwareItem) => {
        urlMap[item.firmware_version] = item.firmware_url;
      });

      // Update state with fetched versions
      setFirmwareVersions(prev => ({
        ...prev,
        [nodeName]: {
          loading: false,
          error: '',
          versions: [...new Set(versions)], // Remove duplicates
          urls: urlMap,
        }
      }));
    } catch (err) {
      console.error(`Failed to fetch firmware versions for ${nodeName}:`, err);
      setFirmwareVersions(prev => ({
        ...prev,
        [nodeName]: {
          ...prev[nodeName] || {},
          loading: false,
          error: 'Failed to fetch firmware versions',
          versions: [],
          urls: {},
        }
      }));
    }
  };

  // Fetch firmware data when filters or pagination changes
  const fetchFirmwares = async () => {
    try {
      setIsLoading(true);
      setError("");

      const response = await FirmwareController.getAllFirmware(
        currentPage,
        pageSize,
        {
          nodeId: selectedNodeId,
          nodeLocation: selectedLocation,
          sensorType: selectedSensorType,
        },
      );

      if (response && response.firmwareData) {
        setFirmwares(response.firmwareData);
        setTotalPages(response.totalPage || 1);
        setTotalData(response.totalData || 0);
        
        // Only update filter options if they exist
        if (response.filterOptions) {
          setFilterOptions({
            nodeId: response.filterOptions.nodeId || [],
            nodeLocation: response.filterOptions.nodeLocation || [],
            sensorType: response.filterOptions.sensorType || [],
          });
        }

        // Fetch firmware versions for each node
        response.firmwareData.forEach(firmware => {
          if (firmware.nodeName) {
            fetchFirmwareVersions(firmware.nodeName);
          }
        });
      } else {
        setFirmwares(response.firmwareData);
        setTotalPages(response.totalPage);
        setTotalData(response.totalData);
        setFilterOptions(response.filterOptions);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to fetch firmware data");
      }

      setFirmwares([]);
      setTotalPages(0);
      setTotalData(0);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Initial fetch on component mount and when filters or pagination changes
  useEffect(() => {
    fetchFirmwares();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    currentPage,
    pageSize,
    selectedNodeId,
    selectedLocation,
    selectedSensorType,
  ]);

  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };
  
  // Handle firmware version change
  const handleVersionChange = async (firmware: Firmware, newVersion: string) => {
    try {
      setIsLoading(true);
      setError("");

      // Get the URL for the selected version
      const url = firmwareVersions[firmware.nodeName]?.urls[newVersion];
      
      // Update firmware with new version and URL
      const updatedFirmware = {
        ...firmware,
        firmwareVersion: newVersion,
        firmwareUrl: url,
      };
      
      // Update the firmware
      await FirmwareController.publishFirmwareUpdate(updatedFirmware);

      // Refresh data
      fetchFirmwares();
      
      setSuccessMessage(
        `Firmware version for ${firmware.nodeName} changed to ${newVersion} successfully!`
      );
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        setSuccessMessage("");
      }, 5000);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to update firmware version");
      } else {
        setError("An unknown error occurred while updating firmware version");
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  // Start editing description
  const startEditingDescription = (firmware: Firmware) => {
    setEditingDescription({
      isEditing: true,
      nodeName: firmware.nodeName,
      description: firmware.firmwareDescription || "",
    });
  };
  
  // Cancel editing description
  const cancelEditingDescription = () => {
    setEditingDescription({
      isEditing: false,
      nodeName: null,
      description: "",
    });
  };
  
  // Handle description change
  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditingDescription(prev => ({
      ...prev,
      description: e.target.value,
    }));
  };
  
  // Save description
  const saveDescription = async () => {
    if (!editingDescription.nodeName) return;
    
    try {
      setIsLoading(true);
      setError("");
      
      // Find the firmware to update
      const firmware = firmwares.find(f => f.nodeName === editingDescription.nodeName);
      
      if (!firmware) {
        setError("Firmware not found");
        return;
      }
      
      // Update description in backend
      await fetchWithAuth(`/firmware/update/${editingDescription.nodeName}`, {
        method: "PUT",
        body: JSON.stringify({
          firmware_description: editingDescription.description
        }),
      });
      
      // Update local data
      const updatedFirmwares = firmwares.map(f => 
        f.nodeName === editingDescription.nodeName 
          ? { ...f, firmwareDescription: editingDescription.description } 
          : f
      );
      
      setFirmwares(updatedFirmwares);
      
      // Reset editing state
      setEditingDescription({
        isEditing: false,
        nodeName: null,
        description: "",
      });
      
      setSuccessMessage("Description updated successfully");
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        setSuccessMessage("");
      }, 5000);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to update description");
      } else {
        setError("An unknown error occurred while updating description");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handle publishing firmware update
  const handlePublishUpdate = async (firmware: Firmware) => {
    try {
      setIsLoading(true);
      setError("");

      // Call the actual API endpoint to publish the firmware update
      await FirmwareController.publishFirmwareUpdate(firmware);

      setSuccessMessage(
        `Firmware update for ${firmware.nodeName} has been published successfully!`,
      );

      // Clear success message after 5 seconds
      setTimeout(() => {
        setSuccessMessage("");
      }, 5000);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to publish firmware update");
      } else {
        setError("An unknown error occurred while publishing firmware update");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handle deleting firmware
  const handleDeleteFirmware = async (nodeName: string) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this firmware? This action cannot be undone.",
      )
    ) {
      return;
    }

    try {
      setIsLoading(true);
      setError("");

      // Call the actual API endpoint to delete the firmware
      await FirmwareController.deleteFirmware(nodeName);

      // Refresh data
      fetchFirmwares();

      setSuccessMessage(`Firmware ${nodeName} has been deleted successfully!`);

      // Clear success message after 5 seconds
      setTimeout(() => {
        setSuccessMessage("");
      }, 5000);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to delete firmware");
      } else {
        setError("An unknown error occurred while deleting firmware");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Filter options for selects
  const nodeIdOptions = [
    { value: "", label: "All Node IDs" },
    ...filterOptions.nodeId.map((id) => ({
      value: id.toString(),
      label: `Node ${id}`,
    })),
  ];

  const locationOptions = [
    { value: "", label: "All Locations" },
    ...filterOptions.nodeLocation.map((location) => ({
      value: location,
      label: location,
    })),
  ];

  const sensorTypeOptions = [
    { value: "", label: "All Sensor Types" },
    ...filterOptions.sensorType.map((type) => ({ value: type, label: type })),
  ];

  // Handle filter changes
  const handleNodeIdChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value ? parseInt(e.target.value) : undefined;
    setSelectedNodeId(value);
    setCurrentPage(1); // Reset to first page when filter changes
  };

  const handleLocationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value || undefined;
    setSelectedLocation(value);
    setCurrentPage(1);
  };

  const handleSensorTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value || undefined;
    setSelectedSensorType(value);
    setCurrentPage(1);
  };

  return (
    <Layout title="Dashboard">
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-3xl font-bold text-lokasync-accent mb-4 sm:mb-0">
          Firmware Dashboard
        </h1>
        <div className="flex flex-col sm:flex-row gap-2">
          <Link to="/firmware/add">
            <Button variant="primary">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-2"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
                  clipRule="evenodd"
                />
              </svg>
              Add Firmware
            </Button>
          </Link>
        </div>
      </div>

      {error && (
        <Alert type="error" message={error} onClose={() => setError("")} />
      )}

      {successMessage && (
        <Alert
          type="success"
          message={successMessage}
          onClose={() => setSuccessMessage("")}
        />
      )}

      <Card>
        {/* Filters */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Select
            label="Node ID"
            options={nodeIdOptions}
            value={selectedNodeId?.toString() || ""}
            onChange={handleNodeIdChange}
          />

          <Select
            label="Location"
            options={locationOptions}
            value={selectedLocation || ""}
            onChange={handleLocationChange}
          />

          <Select
            label="Sensor Type"
            options={sensorTypeOptions}
            value={selectedSensorType || ""}
            onChange={handleSensorTypeChange}
          />
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-lokasync-light-green">
                <th className="border-b border-lokasync-border px-4 py-2 text-left">
                  Node ID
                </th>
                <th className="border-b border-lokasync-border px-4 py-2 text-left">
                  Node Location
                </th>
                <th className="border-b border-lokasync-border px-4 py-2 text-left">
                  Firmware Version
                </th>
                <th className="border-b border-lokasync-border px-4 py-2 text-left">
                  Firmware Description
                </th>
                <th className="border-b border-lokasync-border px-4 py-2 text-left">
                  Sensor Type
                </th>
                <th className="border-b border-lokasync-border px-4 py-2 text-center">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="text-center py-4">
                    <div className="flex justify-center items-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-lokasync-primary"></div>
                      <span className="ml-2">Loading...</span>
                    </div>
                  </td>
                </tr>
              ) : !firmwares.length || firmwares.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-4 text-gray-500">
                    No firmware data found
                  </td>
                </tr>
              ) : (
                firmwares.map((firmware, index) => (
                  <tr
                    key={firmware.nodeName || `firmware-${index}`}
                    className={index % 2 === 0 ? "bg-white" : "bg-gray-50"}
                  >
                    <td className="border-b border-lokasync-border px-4 py-3">
                      {firmware.nodeId}
                    </td>
                    <td className="border-b border-lokasync-border px-4 py-3">
                      {firmware.nodeLocation}
                    </td>
                    <td className="border-b border-lokasync-border px-4 py-3">
                      {firmware.nodeName && firmwareVersions[firmware.nodeName] ? (
                        firmwareVersions[firmware.nodeName].loading ? (
                          <div className="flex items-center">
                            <div className="w-4 h-4 border-2 border-lokasync-primary border-t-transparent rounded-full animate-spin mr-2"></div>
                            <span>Loading versions...</span>
                          </div>
                        ) : firmwareVersions[firmware.nodeName].error ? (
                          <div className="text-red-500">
                            {firmwareVersions[firmware.nodeName].error}
                          </div>
                        ) : (
                          <select
                            className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-lokasync-primary"
                            value={firmware.firmwareVersion}
                            onChange={(e) => handleVersionChange(firmware, e.target.value)}
                          >
                            {firmwareVersions[firmware.nodeName].versions.map(version => (
                              <option key={version} value={version}>
                                {version}
                              </option>
                            ))}
                          </select>
                        )
                      ) : (
                        firmware.firmwareVersion
                      )}
                    </td>
                    <td className="border-b border-lokasync-border px-4 py-3">
                      {editingDescription.isEditing && editingDescription.nodeName === firmware.nodeName ? (
                        <div className="flex flex-col">
                          <textarea
                            ref={textareaRef}
                            className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-lokasync-primary mb-1"
                            value={editingDescription.description}
                            onChange={handleDescriptionChange}
                            maxLength={255}
                            rows={3}
                          ></textarea>
                          <div className="flex justify-end space-x-2 text-xs">
                            <span className="text-gray-500">{editingDescription.description.length}/255</span>
                            <button
                              onClick={cancelEditingDescription}
                              className="text-red-500 hover:text-red-700"
                              title="Cancel"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                              </svg>
                            </button>
                            <button
                              onClick={saveDescription}
                              className="text-green-500 hover:text-green-700"
                              title="Save"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between group">
                          <div className="mr-2 truncate">{firmware.firmwareDescription || "No description"}</div>
                          <button
                            onClick={() => startEditingDescription(firmware)}
                            className="text-gray-400 hover:text-lokasync-primary opacity-0 group-hover:opacity-100 transition-opacity"
                            title="Edit Description"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                            </svg>
                          </button>
                        </div>
                      )}
                    </td>
                    <td className="border-b border-lokasync-border px-4 py-3">
                      {firmware.sensorType}
                    </td>
                    <td className="border-b border-lokasync-border px-4 py-3">
                      <div className="flex justify-center space-x-2">
                        {/* Publish firmware update button */}
                        <button
                          onClick={() => handlePublishUpdate(firmware)}
                          className="text-lokasync-primary hover:text-lokasync-secondary p-1"
                          title="Publish Firmware Update"
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path
                              fillRule="evenodd"
                              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </button>

                        {/* Download URL */}
                        <a
                          href={firmware.firmwareUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-500 hover:text-blue-700 p-1"
                          title="Download Firmware"
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path
                              fillRule="evenodd"
                              d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </a>

                        {/* Delete button */}
                        <button
                          onClick={() =>
                            handleDeleteFirmware(firmware.nodeName)
                          }
                          className="text-red-500 hover:text-red-700 p-1"
                          title="Delete Firmware"
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path
                              fillRule="evenodd"
                              d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="mt-4 flex flex-col sm:flex-row justify-between items-center">
          <div className="mb-4 sm:mb-0">
            <p className="text-sm text-gray-500">
              Showing{" "}
              {firmwares.length > 0 ? (currentPage - 1) * pageSize + 1 : 0} -{" "}
              {Math.min(currentPage * pageSize, totalData)} of {totalData}{" "}
              results
            </p>
          </div>

          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        </div>
      </Card>
    </Layout>
  );
};

export default Dashboard;