import React, { useState } from 'react';
import AddIcon from '../icons/add-icon.tsx';
import { createPreference } from '../../api/fetch_preferences.ts'; 
import{ Preference, UserPreferencesFormProps } from '../../types/pref.ts'
import './form.css';


  
const UserPreferencesForm: React.FC<UserPreferencesFormProps> = ({ setCurrentPage }) => {
  const [preferences, setPreferences] = useState<Preference[]>([{ preference_type: '', preference_value: '' }]);
  const [error, setError] = useState<string | null>(null);

  const handlePreferenceChange = (index: number, field: string, value: string) => {
    setPreferences(prevPreferences =>
      prevPreferences.map((pref, i) =>
        i === index ? { ...pref, [field]: value } : pref
      )
    );
  };

  const addPreference = () => {
    setPreferences([...preferences, { preference_type: '', preference_value: '' }]);
  };

  const handlePreferenceSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) {
      setError('User not authenticated');
      return;
    }

    try {
      for (const pref of preferences) {
        await createPreference({ preference_type: pref.preference_type, preference_value: pref.preference_value }, token);
      }
      setCurrentPage('home'); 
    } catch (err) {
      console.error(err.message);
      setError('Failed to submit preferences');
    }
  };

  const handleSkip = () => {
    setCurrentPage('home'); 
  };

  return (
    <div className="form-container-preferences">
      <div className='pref-title'>Set Your Preferences</div>
      <form onSubmit={handlePreferenceSubmit}>
        {preferences.map((pref, index) => (
          <div key={index}>
            <div className="form-group">
              <label htmlFor={`preferenceType-${index}`}>Preference Type</label>
              <div className="preference-dropdown">
                <div className="dropdown-header" onClick={() => handlePreferenceChange(index, 'preference_type', pref.preference_type ? '' : 'open')}>
                  {pref.preference_type && pref.preference_type !== 'open' ? pref.preference_type : 'Select a preference type'}
                </div>
                {pref.preference_type === 'open' && (
                  <div className="dropdown-menu">
                    <div className="dropdown-item" onClick={() => handlePreferenceChange(index, 'preference_type', 'author')}>Author</div>
                    <div className="dropdown-item" onClick={() => handlePreferenceChange(index, 'preference_type', 'genre')}>Genre</div>
                  </div>
                )}
              </div>
            </div>
            {pref.preference_type && pref.preference_type !== 'open' && (
              <div className="form-group">
                <label htmlFor={`preferenceValue-${index}`}>Specify {pref.preference_type}</label>
                <input
                  type="text"
                  id={`preferenceValue-${index}`}
                  name={`preferenceValue-${index}`}
                  placeholder={`Enter ${pref.preference_type}`}
                  required
                  value={pref.preference_value}
                  onChange={(e) => handlePreferenceChange(index, 'preference_value', e.target.value)}
                />
              </div>
            )}
          </div>
        ))}
        {error && <div className="error">{error}</div>}
        <div className="add-preference">
          <AddIcon onClick={addPreference} />
        </div>
        <div className='pref-buttons'>
          <button type="submit">Submit Preferences</button>
          <button type="button" onClick={handleSkip}>Skip</button>
        </div>
      </form>
    </div>
  );
};
  
    export default UserPreferencesForm;