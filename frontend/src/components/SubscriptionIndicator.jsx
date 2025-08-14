import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/solid';

const SubscriptionIndicator = ({ user }) => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchSubscription();
    }
  }, [user]);

  const fetchSubscription = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/current`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setSubscription(data);
      }
    } catch (error) {
      console.error('Error fetching subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !subscription?.subscription) return null;

  const { subscription: sub } = subscription;
  const isTrialExpiringSoon = sub.is_trial && sub.days_remaining <= 3;
  const isExpired = sub.status === 'expired';

  if (isExpired || isTrialExpiringSoon) {
    return (
      <Link
        to="/billing"
        className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
          isExpired
            ? 'bg-red-100 text-red-800 hover:bg-red-200'
            : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
        }`}
      >
        <ExclamationTriangleIcon className={`w-4 h-4 mr-2 ${isExpired ? 'text-red-500' : 'text-yellow-500'}`} />
        {isExpired ? 'Subscription Expired' : `${sub.days_remaining} days left`}
      </Link>
    );
  }

  if (sub.is_trial) {
    return (
      <Link
        to="/billing"
        className="flex items-center px-3 py-2 rounded-lg bg-blue-100 text-blue-800 hover:bg-blue-200 text-sm font-medium transition-colors"
      >
        <CheckCircleIcon className="w-4 h-4 mr-2 text-blue-500" />
        Trial: {sub.days_remaining} days
      </Link>
    );
  }

  return (
    <Link
      to="/billing"
      className="flex items-center px-3 py-2 rounded-lg bg-green-100 text-green-800 hover:bg-green-200 text-sm font-medium transition-colors"
    >
      <CheckCircleIcon className="w-4 h-4 mr-2 text-green-500" />
      {sub.tier} Plan
    </Link>
  );
};

export default SubscriptionIndicator;