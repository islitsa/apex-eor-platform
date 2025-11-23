import React from 'react';

interface FileActionButtonsProps {
  filePath: string;
  fileName: string;
}

export default function FileActionButtons({ filePath, fileName }: FileActionButtonsProps) {
  const handleDownload = () => {
    console.log('Download file:', filePath);
    alert(`Download functionality for: ${fileName}\nPath: ${filePath}`);
  };

  const handleView = () => {
    console.log('View file:', filePath);
    alert(`View functionality for: ${fileName}\nPath: ${filePath}`);
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleView}
        className="flex items-center gap-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        style={{ height: '40px', borderRadius: '16px' }}
        title="View file"
      >
        <span className="material-symbols-rounded text-lg" style={{ marginLeft: '4px' }}>
          visibility
        </span>
        <span className="text-sm font-medium">View</span>
      </button>
      
      <button
        onClick={handleDownload}
        className="flex items-center gap-1 px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        style={{ height: '40px', borderRadius: '16px' }}
        title="Download file"
      >
        <span className="material-symbols-rounded text-lg">cloud_download</span>
        <span className="text-sm font-medium">Download</span>
      </button>
    </div>
  );
}