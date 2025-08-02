import React, { useState } from "react";
import Dropzone from "react-dropzone";
import axios from "axios";
import Select from "react-select";
import "./App.css";

const ENTITY_OPTIONS = [
  "person", "email_address", "phone", "address", "city", "country",
  "id_number", "credit_card", "account_number", "license_number",
  "organization", "date", "time", "doctor", "patient_id", "dob",
  "location", "medical_condition", "body_part", "age"
].map((tag) => ({ value: tag, label: tag }));

function App() {
  const [file, setFile] = useState(null);
  const [selectedTags, setSelectedTags] = useState(ENTITY_OPTIONS);
  const [status, setStatus] = useState("");
  const [redactedPdfUrl, setRedactedPdfUrl] = useState(null);

  const handleDrop = (acceptedFiles) => {
    setFile(acceptedFiles[0]);
    setRedactedPdfUrl(null);
    setStatus("");
  };

  const handleSubmit = async () => {
    setStatus("🔄 Processing...");
    const formData = new FormData();
    formData.append("pdf", file);
    formData.append("tags", JSON.stringify(selectedTags.map(tag => tag.value)));

    try {
      const response = await axios.post("http://localhost:8000/redact", formData, {
        responseType: "blob",
      });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      setRedactedPdfUrl(url);
      setStatus("✅ Redaction complete.");
    } catch (err) {
      console.error(err);
      setStatus("❌ Something went wrong.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white font-inter p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-extrabold mb-4 text-center text-blue-400 tracking-tight">
          SafeDocs: Automated PDF Redactor
        </h1>
        <p className="text-center text-gray-400 mb-8 leading-relaxed">
          Upload a PDF document and select the entities you want to hide.
          SafeDocs will automatically detect and redact sensitive information
          for you — keeping privacy simple and secure.
        </p>

        {/* Dropzone */}
        <div className="bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
          <Dropzone onDrop={handleDrop} accept={{ "application/pdf": [".pdf"] }}>
            {({ getRootProps, getInputProps }) => (
              <div
                {...getRootProps()}
                className="border-2 border-dashed border-gray-600 hover:border-blue-500 transition-colors p-8 rounded-xl text-center cursor-pointer"
              >
                <input {...getInputProps()} />
                <p className="text-gray-300">
                  {file ? (
                    <span className="text-white font-medium">{file.name}</span>
                  ) : (
                    "📄 Drag and drop your PDF here, or click to upload"
                  )}
                </p>
              </div>
            )}
          </Dropzone>
        </div>

        {/* Tag Selector */}
        <div className="bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-100 mb-2">🔍 Select What You Want Hidden</h2>
          <Select
            isMulti
            value={selectedTags}
            onChange={setSelectedTags}
            options={ENTITY_OPTIONS}
            className="text-black rounded"
          />
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={!file}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 px-6 py-3 rounded-xl font-medium transition-colors"
        >
          🚀 Redact PDF
        </button>

        {/* Status */}
        {status && (
          <p className="mt-4 text-center text-sm text-gray-400">{status}</p>
        )}

        {/* Download */}
        {redactedPdfUrl && (
          <a
            href={redactedPdfUrl}
            download="redacted.pdf"
            className="block mt-6 bg-green-600 hover:bg-green-700 px-6 py-3 rounded-xl text-center font-medium transition-colors"
          >
            ⬇️ Download Redacted PDF
          </a>
        )}
      </div>
    </div>
  );
}

export default App;

