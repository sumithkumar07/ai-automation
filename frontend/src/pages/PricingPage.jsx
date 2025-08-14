import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { CheckIcon, XMarkIcon, ArrowRightIcon } from '@heroicons/react/24/solid';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const PricingPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [plans, setPlans] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/plans`);
      if (response.ok) {
        const data = await response.json();
        setPlans(data.plans);
      }
    } catch (error) {
      console.error('Error fetching plans:', error);
      toast.error('Failed to load pricing plans');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (tierName) => {
    if (!user) {
      navigate('/auth');
      return;
    }

    setUpgrading(tierName);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/upgrade`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          tier: tierName,
          billing_cycle: billingCycle,
          origin_url: window.location.origin
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.checkout && data.checkout.checkout_url) {
          window.location.href = data.checkout.checkout_url;
        } else {
          toast.error('Failed to create checkout session');
        }
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Failed to start upgrade process');
      }
    } catch (error) {
      console.error('Error starting upgrade:', error);
      toast.error('Failed to start upgrade process');
    } finally {
      setUpgrading(null);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(price);
  };

  const calculateMonthlySavings = (plan) => {
    if (billingCycle === 'yearly') {
      return plan.yearly_savings;
    }
    return 0;
  };

  const getPrice = (plan) => {
    return billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  };

  const getDisplayPrice = (plan) => {
    const price = getPrice(plan);
    if (billingCycle === 'yearly') {
      return `${formatPrice(price / 12)}/month`;
    }
    return `${formatPrice(price)}/month`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <Link to="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-bold text-gray-900">Aether Automation</span>
            </Link>
            <div className="flex items-center space-x-4">
              {user ? (
                <Link
                  to="/dashboard"
                  className="text-gray-600 hover:text-gray-900 font-medium"
                >
                  Dashboard
                </Link>
              ) : (
                <Link
                  to="/auth"
                  className="text-gray-600 hover:text-gray-900 font-medium"
                >
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-12">
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Start with a 7-day free trial. No credit card required. Scale as you grow.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center mb-12">
            <div className="bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  billingCycle === 'monthly'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors relative ${
                  billingCycle === 'yearly'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Yearly
                <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                  Save 17%
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Pricing Cards */}
        {plans && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {Object.entries(plans).map(([tierKey, plan]) => {
              const isPopular = tierKey === 'pro';
              const savings = calculateMonthlySavings(plan);
              
              return (
                <div
                  key={tierKey}
                  className={`relative bg-white rounded-2xl shadow-lg border-2 transition-transform hover:scale-105 ${
                    isPopular ? 'border-blue-500 ring-4 ring-blue-500 ring-opacity-20' : 'border-gray-200'
                  }`}
                >
                  {isPopular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                        Most Popular
                      </span>
                    </div>
                  )}

                  <div className="p-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                    
                    <div className="mb-6">
                      <div className="flex items-baseline">
                        <span className="text-4xl font-bold text-gray-900">
                          {getDisplayPrice(plan)}
                        </span>
                        {billingCycle === 'yearly' && (
                          <span className="text-sm text-gray-500 ml-2">
                            billed yearly
                          </span>
                        )}
                      </div>
                      {billingCycle === 'yearly' && savings > 0 && (
                        <p className="text-sm text-green-600 mt-1">
                          Save {formatPrice(savings)} per year
                        </p>
                      )}
                      {tierKey === 'basic' && (
                        <p className="text-sm text-blue-600 mt-1 font-medium">
                          7-day free trial included
                        </p>
                      )}
                    </div>

                    <button
                      onClick={() => handleUpgrade(tierKey)}
                      disabled={upgrading === tierKey}
                      className={`w-full py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center ${
                        isPopular
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white'
                          : 'bg-gray-900 hover:bg-gray-800 text-white'
                      } ${upgrading === tierKey ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      {upgrading === tierKey ? (
                        <LoadingSpinner size="small" color="white" />
                      ) : (
                        <>
                          {user ? 'Upgrade Now' : 'Start Free Trial'}
                          <ArrowRightIcon className="w-4 h-4 ml-2" />
                        </>
                      )}
                    </button>

                    <div className="mt-8">
                      <h4 className="text-sm font-semibold text-gray-900 mb-4 uppercase tracking-wide">
                        Features
                      </h4>
                      <ul className="space-y-3">
                        {plan.features.map((feature, index) => (
                          <li key={index} className="flex items-start">
                            <CheckIcon className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-gray-600">{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* FAQ Section */}
        <div className="mt-20">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Can I change my plan at any time?
              </h3>
              <p className="text-gray-600">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                What happens after my trial ends?
              </h3>
              <p className="text-gray-600">
                Your workflows will be paused until you choose a paid plan. Your data is safely stored and accessible once you upgrade.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Do you offer refunds?
              </h3>
              <p className="text-gray-600">
                Yes, we offer a 30-day money-back guarantee for all paid plans. No questions asked.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Is my data secure?
              </h3>
              <p className="text-gray-600">
                Absolutely. We use enterprise-grade encryption and security measures to protect your data.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-20 text-center">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Automate Your Workflows?
            </h2>
            <p className="text-xl mb-6 opacity-90">
              Start your 7-day free trial today. No credit card required.
            </p>
            {!user && (
              <Link
                to="/auth"
                className="inline-flex items-center px-6 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
              >
                Get Started Free
                <ArrowRightIcon className="w-5 h-5 ml-2" />
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;