import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Customers = () => {
  const [customers, setCustomers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await axios.get('/api/customers/');
      setCustomers(response.data);
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  const handleViewCustomer = async (customerId) => {
    try {
      const response = await axios.get(`/api/customers/${customerId}`);
      setSelectedCustomer(response.data);
    } catch (error) {
      console.error('Error fetching customer details:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    try {
      await axios.post('/api/customers/', data);
      fetchCustomers();
      setShowModal(false);
    } catch (error) {
      console.error('Error creating customer:', error);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Customers</h1>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Customer
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date Added</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {customers.map((customer) => (
              <tr key={customer.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <div className="font-medium">{customer.full_name}</div>
                    {customer.business_name && (
                      <div className="text-sm text-gray-500">{customer.business_name}</div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                    {customer.customer_type}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-500">{customer.phone || '-'}</td>
                <td className="px-6 py-4 text-gray-500">{customer.email || '-'}</td>
                <td className="px-6 py-4 text-gray-500">{customer.date_added}</td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => handleViewCustomer(customer.id)}
                    className="text-blue-600 hover:text-blue-900 mr-2"
                  >
                    View Details
                  </button>
                  <button
                    onClick={() => {/* Send document */}}
                    className="text-green-600 hover:text-green-900"
                  >
                    Send Document
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Add New Customer</h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Full Name</label>
                <input name="full_name" type="text" className="w-full border rounded px-3 py-2" required />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Business Name (Optional)</label>
                <input name="business_name" type="text" className="w-full border rounded px-3 py-2" />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Customer Type</label>
                <select name="customer_type" className="w-full border rounded px-3 py-2">
                  <option value="individual">Individual</option>
                  <option value="business">Business</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Phone</label>
                <input name="phone" type="text" className="w-full border rounded px-3 py-2" />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Email</label>
                <input name="email" type="email" className="w-full border rounded px-3 py-2" />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">TIN (Optional)</label>
                <input name="tin" type="text" className="w-full border rounded px-3 py-2" />
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
                  Add Customer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {selectedCustomer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-screen overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Customer Details</h2>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-sm text-gray-500">Name</label>
                <p className="font-medium">{selectedCustomer.customer.full_name}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Business Name</label>
                <p className="font-medium">{selectedCustomer.customer.business_name || '-'}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Type</label>
                <p className="font-medium">{selectedCustomer.customer.customer_type}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">TIN</label>
                <p className="font-medium">{selectedCustomer.customer.tin || '-'}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Phone</label>
                <p className="font-medium">{selectedCustomer.customer.phone || '-'}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Email</label>
                <p className="font-medium">{selectedCustomer.customer.email || '-'}</p>
              </div>
            </div>
            
            <div className="mt-6">
              <h3 className="font-semibold mb-2">Purchase History</h3>
              <p className="text-sm text-gray-500 mb-2">Total Purchased: TZS {selectedCustomer.total_purchased?.toLocaleString()}</p>
              <p className="text-sm text-gray-500 mb-4">Last Purchase: {selectedCustomer.last_purchase_date || 'Never'}</p>
              
              {selectedCustomer.sales_history && selectedCustomer.sales_history.length > 0 ? (
                <table className="min-w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Date</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {selectedCustomer.sales_history.map((sale, index) => (
                      <tr key={index}>
                        <td className="px-4 py-2">{sale.sale_date}</td>
                        <td className="px-4 py-2">TZS {sale.amount?.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="text-gray-500">No purchase history</p>
              )}
            </div>
            
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setSelectedCustomer(null)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Customers;