import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CompanyCare = () => {
  const [summary, setSummary] = useState(null);
  const [debtors, setDebtors] = useState([]);
  const [creditors, setCreditors] = useState([]);
  const [activeTab, setActiveTab] = useState('summary');
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [summaryRes, debtorsRes, creditorsRes] = await Promise.all([
        axios.get('/api/company-care/summary'),
        axios.get('/api/company-care/debtors'),
        axios.get('/api/company-care/creditors')
      ]);
      setSummary(summaryRes.data);
      setDebtors(debtorsRes.data);
      setCreditors(creditorsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800';
      case 'watch': return 'bg-yellow-100 text-yellow-800';
      case 'at_risk': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Company Care</h1>

      <div className="mb-4">
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('summary')}
            className={`px-4 py-2 ${activeTab === 'summary' ? 'border-b-2 border-blue-600 text-blue-600' : ''}`}
          >
            Summary
          </button>
          <button
            onClick={() => setActiveTab('debtors')}
            className={`px-4 py-2 ${activeTab === 'debtors' ? 'border-b-2 border-blue-600 text-blue-600' : ''}`}
          >
            Debtors ({debtors.length})
          </button>
          <button
            onClick={() => setActiveTab('creditors')}
            className={`px-4 py-2 ${activeTab === 'creditors' ? 'border-b-2 border-blue-600 text-blue-600' : ''}`}
          >
            Creditors ({creditors.length})
          </button>
        </div>
      </div>

      {activeTab === 'summary' && summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Debtors</h3>
            <p className="text-2xl font-bold text-green-600">TZS {summary.total_debtors?.toLocaleString()}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Creditors</h3>
            <p className="text-2xl font-bold text-red-600">TZS {summary.total_creditors?.toLocaleString()}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Net Position</h3>
            <p className={`text-2xl font-bold ${summary.net_position >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              TZS {summary.net_position?.toLocaleString()}
            </p>
            <span className={`px-2 py-1 rounded text-xs mt-2 inline-block ${getHealthStatusColor(summary.health_status)}`}>
              {summary.health_status?.toUpperCase()}
            </span>
          </div>
        </div>
      )}

      {activeTab === 'debtors' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 flex justify-between">
            <h2 className="text-lg font-semibold">Debtors</h2>
            <button
              onClick={() => setShowModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              + Add Debtor
            </button>
          </div>
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount Owed</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount Paid</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Balance</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {debtors.map((debtor) => (
                <tr key={debtor.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">{debtor.debtor_name}</td>
                  <td className="px-6 py-4">TZS {debtor.amount_owed?.toLocaleString()}</td>
                  <td className="px-6 py-4">TZS {debtor.amount_paid?.toLocaleString()}</td>
                  <td className="px-6 py-4 font-semibold">TZS {debtor.balance_remaining?.toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs ${
                      debtor.status === 'paid' ? 'bg-green-100 text-green-800' :
                      debtor.status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {debtor.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-blue-600 hover:text-blue-900">Record Payment</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'creditors' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 flex justify-between">
            <h2 className="text-lg font-semibold">Creditors</h2>
            <button
              onClick={() => setShowModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              + Add Creditor
            </button>
          </div>
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount Owed</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount Paid</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Balance</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {creditors.map((creditor) => (
                <tr key={creditor.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">{creditor.creditor_name}</td>
                  <td className="px-6 py-4">TZS {creditor.amount_owed?.toLocaleString()}</td>
                  <td className="px-6 py-4">TZS {creditor.amount_paid?.toLocaleString()}</td>
                  <td className="px-6 py-4 font-semibold">TZS {creditor.balance_remaining?.toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs ${
                      creditor.status === 'paid' ? 'bg-green-100 text-green-800' :
                      creditor.status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {creditor.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-blue-600 hover:text-blue-900">Record Payment</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Add New {activeTab === 'debtors' ? 'Debtor' : 'Creditor'}</h2>
            <form onSubmit={async (e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const data = Object.fromEntries(formData);
              try {
                await axios.post(`/api/company-care/${activeTab}`, data);
                fetchData();
                setShowModal(false);
              } catch (error) {
                console.error('Error:', error);
              }
            }}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Name</label>
                <input name="name" type="text" className="w-full border rounded px-3 py-2" required />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Amount Owed</label>
                <input name="amount_owed" type="number" className="w-full border rounded px-3 py-2" required />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded"
                >
                  Add
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompanyCare;