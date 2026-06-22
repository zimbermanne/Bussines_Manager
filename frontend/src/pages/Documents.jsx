import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState('inbox');
  const [showModal, setShowModal] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, [activeTab]);

  const fetchDocuments = async () => {
    try {
      const endpoint = activeTab === 'inbox' ? '/api/documents/inbox' : '/api/documents/outbox';
      const response = await axios.get(endpoint);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleViewDocument = (doc) => {
    setSelectedDoc(doc);
    setShowModal(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'delivered': return 'bg-blue-100 text-blue-800';
      case 'sent': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDocumentTypeLabel = (type) => {
    const labels = {
      'QUO': 'Quotation',
      'PRO': 'Proforma Invoice',
      'INV': 'Invoice',
      'RCP': 'Receipt',
      'CRN': 'Credit Note',
      'DBN': 'Debit Note',
      'DLN': 'Delivery Note'
    };
    return labels[type] || type;
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Business Documents</h1>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + New Document
        </button>
      </div>

      <div className="mb-4">
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('inbox')}
            className={`px-4 py-2 ${activeTab === 'inbox' ? 'border-b-2 border-blue-600 text-blue-600' : ''}`}
          >
            Inbox ({documents.length})
          </button>
          <button
            onClick={() => setActiveTab('outbox')}
            className={`px-4 py-2 ${activeTab === 'outbox' ? 'border-b-2 border-blue-600 text-blue-600' : ''}`}
          >
            Outbox ({documents.length})
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Document Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Number</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <tr key={doc.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-medium">{getDocumentTypeLabel(doc.document_type)}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-500">{doc.document_number}</td>
                <td className="px-6 py-4 whitespace-nowrap">{doc.client_name}</td>
                <td className="px-6 py-4 whitespace-nowrap font-semibold">
                  {doc.currency === 'TZS' ? 'TZS ' : ''}{doc.grand_total?.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-500">{doc.issue_date}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColor(doc.status)}`}>
                    {doc.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => handleViewDocument(doc)}
                    className="text-blue-600 hover:text-blue-900 mr-2"
                  >
                    View
                  </button>
                  {activeTab === 'inbox' && doc.status === 'delivered' && (
                    <>
                      <button
                        onClick={() => confirmDocument(doc.id)}
                        className="text-green-600 hover:text-green-900 mr-2"
                      >
                        Confirm
                      </button>
                      <button
                        onClick={() => rejectDocument(doc.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Reject
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <DocumentModal
          document={selectedDoc}
          onClose={() => setShowModal(false)}
          onSave={fetchDocuments}
        />
      )}
    </div>
  );
};

const DocumentModal = ({ document, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    document_type: 'INV',
    receiver_company_id: '',
    client_name: '',
    client_address: '',
    currency: 'TZS',
    vat_rate: 18,
    items: [{ description: '', quantity: 1, unit_price: 0 }]
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/documents/', formData);
      onSave();
      onClose();
    } catch (error) {
      console.error('Error creating document:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-screen overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Create New Document</h2>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">Document Type</label>
              <select
                value={formData.document_type}
                onChange={(e) => setFormData({...formData, document_type: e.target.value})}
                className="w-full border rounded px-3 py-2"
              >
                <option value="QUO">Quotation</option>
                <option value="PRO">Proforma Invoice</option>
                <option value="INV">Invoice</option>
                <option value="RCP">Receipt</option>
                <option value="CRN">Credit Note</option>
                <option value="DBN">Debit Note</option>
                <option value="DLN">Delivery Note</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Currency</label>
              <select
                value={formData.currency}
                onChange={(e) => setFormData({...formData, currency: e.target.value})}
                className="w-full border rounded px-3 py-2"
              >
                <option value="TZS">TZS</option>
                <option value="USD">USD</option>
                <option value="KES">KES</option>
                <option value="EUR">EUR</option>
              </select>
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Client Name</label>
            <input
              type="text"
              value={formData.client_name}
              onChange={(e) => setFormData({...formData, client_name: e.target.value})}
              className="w-full border rounded px-3 py-2"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Client Address</label>
            <textarea
              value={formData.client_address}
              onChange={(e) => setFormData({...formData, client_address: e.target.value})}
              className="w-full border rounded px-3 py-2"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Items</label>
            {formData.items.map((item, index) => (
              <div key={index} className="grid grid-cols-4 gap-2 mb-2">
                <input
                  type="text"
                  placeholder="Description"
                  value={item.description}
                  onChange={(e) => {
                    const newItems = [...formData.items];
                    newItems[index].description = e.target.value;
                    setFormData({...formData, items: newItems});
                  }}
                  className="border rounded px-3 py-2"
                />
                <input
                  type="number"
                  placeholder="Quantity"
                  value={item.quantity}
                  onChange={(e) => {
                    const newItems = [...formData.items];
                    newItems[index].quantity = parseFloat(e.target.value);
                    setFormData({...formData, items: newItems});
                  }}
                  className="border rounded px-3 py-2"
                />
                <input
                  type="number"
                  placeholder="Unit Price"
                  value={item.unit_price}
                  onChange={(e) => {
                    const newItems = [...formData.items];
                    newItems[index].unit_price = parseFloat(e.target.value);
                    setFormData({...formData, items: newItems});
                  }}
                  className="border rounded px-3 py-2"
                />
                <button
                  type="button"
                  onClick={() => {
                    const newItems = formData.items.filter((_, i) => i !== index);
                    setFormData({...formData, items: newItems});
                  }}
                  className="bg-red-500 text-white rounded px-3 py-2"
                >
                  Remove
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={() => setFormData({...formData, items: [...formData.items, { description: '', quantity: 1, unit_price: 0 }]})}
              className="bg-blue-500 text-white rounded px-3 py-2 text-sm"
            >
              + Add Item
            </button>
          </div>

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-300 text-gray-700 px-4 py-2 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded"
            >
              Create Document
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Documents;