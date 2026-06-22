import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Staff = () => {
  const [employees, setEmployees] = useState([]);
  const [payrollRuns, setPayrollRuns] = useState([]);
  const [activeTab, setActiveTab] = useState('employees');
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (activeTab === 'employees') {
      fetchEmployees();
    } else {
      fetchPayrollRuns();
    }
  }, [activeTab]);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get('/api/staff/employees');
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const fetchPayrollRuns = async () => {
    try {
      const response = await axios.get('/api/staff/payroll-runs');
      setPayrollRuns(response.data);
    } catch (error) {
      console.error('Error fetching payroll runs:', error);
    }
  };

  const handleCreatePayroll = async () => {
    const month = new Date().getMonth() + 1;
    const year = new Date().getFullYear();
    
    try {
      await axios.post('/api/staff/payroll-runs', {
        period_month: month,
        period_year: year
      });
      fetchPayrollRuns();
    } catch (error) {
      console.error('Error creating payroll:', error);
    }
  };

  const handleSubmitEmployee = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    try {
      await axios.post('/api/staff/employees', data);
      fetchEmployees();
      setShowModal(false);
    } catch (error) {
      console.error('Error creating employee:', error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Staff & Payroll Management</h1>

      <div className="mb-4">
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('employees')}
            className={`px-4 py-2 ${activeTab === 'employees' ? 'border-b-2 border-blue-600 text-blue-600' : ''}`}
          >
            Employees ({employees.length})
          </button>
          <button
            onClick={() => setActiveTab('payroll')}
            className={`px-4 py-2 ${activeTab === 'payroll' ? 'border-b-2 border-blue-600 text-blue-600' : ''}`}
          >
            Payroll Runs ({payrollRuns.length})
          </button>
        </div>
      </div>

      {activeTab === 'employees' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 flex justify-between">
            <h2 className="text-lg font-semibold">Employees</h2>
            <button
              onClick={() => setShowModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              + Add Employee
            </button>
          </div>
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Position</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Basic Salary</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {employees.map((employee) => (
                <tr key={employee.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="font-medium">{employee.full_name}</div>
                      <div className="text-sm text-gray-500">{employee.email || ''}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">{employee.position || '-'}</td>
                  <td className="px-6 py-4">{employee.department || '-'}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                      {employee.employment_type || '-'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    TZS {employee.basic_salary?.toLocaleString() || '0'}
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-blue-600 hover:text-blue-900">Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'payroll' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 flex justify-between">
            <h2 className="text-lg font-semibold">Payroll Runs</h2>
            <button
              onClick={handleCreatePayroll}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              + Create New Payroll
            </button>
          </div>
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Gross</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Deductions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Net Pay</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {payrollRuns.map((run) => (
                <tr key={run.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    {run.period_month}/{run.period_year}
                  </td>
                  <td className="px-6 py-4">
                    TZS {run.total_gross_pay?.toLocaleString() || '0'}
                  </td>
                  <td className="px-6 py-4">
                    TZS {run.total_deductions?.toLocaleString() || '0'}
                  </td>
                  <td className="px-6 py-4 font-semibold">
                    TZS {run.total_net_pay?.toLocaleString() || '0'}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs ${
                      run.status === 'paid' ? 'bg-green-100 text-green-800' :
                      run.status === 'finalized' ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {run.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-blue-600 hover:text-blue-900 mr-2">View Details</button>
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
            <h2 className="text-xl font-bold mb-4">Add New Employee</h2>
            <form onSubmit={handleSubmitEmployee}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Full Name</label>
                <input name="full_name" type="text" className="w-full border rounded px-3 py-2" required />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Position</label>
                <input name="position" type="text" className="w-full border rounded px-3 py-2" />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Department</label>
                <input name="department" type="text" className="w-full border rounded px-3 py-2" />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Employment Type</label>
                <select name="employment_type" className="w-full border rounded px-3 py-2">
                  <option value="permanent">Permanent</option>
                  <option value="contract">Contract</option>
                  <option value="casual">Casual</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Employment Date</label>
                <input name="employment_date" type="date" className="w-full border rounded px-3 py-2" required />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Basic Salary</label>
                <input name="basic_salary" type="number" className="w-full border rounded px-3 py-2" />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Phone</label>
                <input name="phone" type="text" className="w-full border rounded px-3 py-2" />
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
                  Add Employee
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Staff;