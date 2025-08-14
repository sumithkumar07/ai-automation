import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  CreditCardIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  CalendarIcon,
  UserGroupIcon,
  CpuChipIcon,
  CloudIcon
} from '@heroicons/react/24/solid';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const BillingPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');

  const [subscription, setSubscription] = useState(null);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processingPayment, setProcessingPayment] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }

    fetchSubscriptionData();

    // Check for successful payment
    if (sessionId) {
      handlePaymentSuccess(sessionId);
    }
  }, [user, sessionId]);

  const fetchSubscriptionData = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      
      // Fetch subscription and usage data in parallel
      const [subResponse, usageResponse] = await Promise.all([
        fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/subscription/current`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/subscription/usage`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (subResponse.ok) {
        const subData = await subResponse.json();
        setSubscription(subData);
      }

      if (usageResponse.ok) {
        const usageData = await usageResponse.json();
        setUsage(usageData.usage);
      }
    } catch (error) {
      console.error('Error fetching subscription data:', error);
      toast.error('Failed to load billing information');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentSuccess = async (sessionId) => {
    setProcessingPayment(true);
    
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/subscription/payment/status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ session_id: sessionId })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.payment_status === 'paid') {
          toast.success('Payment successful! Your subscription has been activated.');
          // Refresh subscription data
          setTimeout(() => fetchSubscriptionData(), 2000);
        } else {
          toast.loading('Processing payment...', { duration: 3000 });
          // Poll for payment status
          setTimeout(() => handlePaymentSuccess(sessionId), 3000);
        }
      } else {
        toast.error('Failed to verify payment status');
      }
    } catch (error) {
      console.error('Error checking payment status:', error);
      toast.error('Failed to verify payment');
    } finally {
      setProcessingPayment(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getUsagePercentage = (current, limit) => {
    if (limit === 0) return 0;
    return Math.min((current / limit) * 100, 100);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'trial': return 'text-blue-600 bg-blue-100';
      case 'expired': return 'text-red-600 bg-red-100';
      case 'cancelled': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Billing & Usage</h1>
          <p className="text-gray-600 mt-2">Manage your subscription and monitor usage</p>
        </div>

        {processingPayment && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center">
              <ArrowPathIcon className="w-5 h-5 text-blue-500 animate-spin mr-2" />
              <span className="text-blue-800">Processing your payment...</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Subscription Status */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Plan</h2>
              
              {subscription && subscription.subscription ? (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 capitalize">
                        {subscription.subscription.tier} Plan
                      </h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${getStatusColor(subscription.subscription.status)}`}>
                        {subscription.subscription.status === 'trial' ? 'Free Trial' : subscription.subscription.status}
                      </span>
                    </div>
                    {!subscription.subscription.is_trial && (
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Next billing date</p>
                        <p className="font-semibold">
                          {subscription.subscription.expires_at && formatDate(subscription.subscription.expires_at)}
                        </p>
                      </div>
                    )}
                  </div>

                  {subscription.subscription.is_trial && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                      <div className="flex items-center">
                        <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500 mr-2" />
                        <div>
                          <p className="font-medium text-yellow-800">
                            {subscription.subscription.days_remaining} days remaining in your free trial
                          </p>
                          <p className="text-sm text-yellow-700 mt-1">
                            Upgrade to continue using Aether Automation after your trial ends.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-4">
                    <button
                      onClick={() => navigate('/pricing')}
                      className="btn-primary"
                    >
                      {subscription.subscription.is_trial ? 'Upgrade Plan' : 'Change Plan'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <CreditCardIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Subscription</h3>
                  <p className="text-gray-600 mb-4">Start your free trial to access all features</p>
                  <button
                    onClick={() => navigate('/pricing')}
                    className="btn-primary"
                  >
                    View Plans
                  </button>
                </div>
              )}
            </div>

            {/* Usage Statistics */}
            {usage && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">Usage This Month</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Workflows */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <CpuChipIcon className="w-5 h-5 text-blue-500 mr-2" />
                        <span className="font-medium">Workflows Created</span>
                      </div>
                      <span className="text-sm text-gray-600">
                        {usage.current_usage.workflows_created || 0} / {usage.limits.workflows_per_month || '∞'}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${usage.percentage_used.workflows_created || 0}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Executions */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <ArrowPathIcon className="w-5 h-5 text-green-500 mr-2" />
                        <span className="font-medium">Executions Run</span>
                      </div>
                      <span className="text-sm text-gray-600">
                        {usage.current_usage.executions_run || 0} / {usage.limits.executions_per_month || '∞'}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${usage.percentage_used.executions_run || 0}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* AI Requests */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <CloudIcon className="w-5 h-5 text-purple-500 mr-2" />
                        <span className="font-medium">AI Requests</span>
                      </div>
                      <span className="text-sm text-gray-600">
                        {usage.current_usage.ai_requests || 0} / {usage.limits.ai_requests_per_month || '∞'}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${usage.percentage_used.ai_requests || 0}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Storage */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <CloudIcon className="w-5 h-5 text-orange-500 mr-2" />
                        <span className="font-medium">Storage Used</span>
                      </div>
                      <span className="text-sm text-gray-600">
                        {((usage.current_usage.storage_used_mb || 0) / 1024).toFixed(1)} GB / {usage.limits.storage_gb || '∞'} GB
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-orange-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(((usage.current_usage.storage_used_mb || 0) / 1024) / (usage.limits.storage_gb || 1) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/pricing')}
                  className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center">
                    <CreditCardIcon className="w-5 h-5 text-gray-400 mr-3" />
                    <span className="font-medium">View All Plans</span>
                  </div>
                </button>
                
                <button
                  onClick={() => window.open('mailto:support@aetheramation.com')}
                  className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center">
                    <UserGroupIcon className="w-5 h-5 text-gray-400 mr-3" />
                    <span className="font-medium">Contact Support</span>
                  </div>
                </button>
              </div>
            </div>

            {/* Usage Tips */}
            <div className="bg-blue-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 Usage Tips</h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li>• Optimize workflows to use fewer steps</li>
                <li>• Use conditional logic to reduce executions</li>
                <li>• Archive old workflows you no longer need</li>
                <li>• Monitor usage regularly to avoid overages</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BillingPage;