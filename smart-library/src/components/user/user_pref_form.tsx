import React, { useState } from 'react';
import AddIcon from '../icons/add-icon.tsx';
import { createPreference } from '../../api/fetch_preferences.ts'; 
import './form.css';

type UserPreferencesFormProps = {
    setCurrentPage: React.Dispatch<React.SetStateAction<string>>;
  };
  
  type Preference = {
    id: number;
    type: string;
    value: string;
  };
  
  const UserPreferencesForm: React.FC<UserPreferencesFormProps> = ({ setCurrentPage }) => {
    const [preferences, setPreferences] = useState<Preference[]>([{ id: Date.now(), type: '', value: '' }]);
    const [error, setError] = useState<string | null>(null);
  
    const handlePreferenceChange = (id: number, field: string, value: string) => {
      setPreferences(prevPreferences =>
        prevPreferences.map(pref =>
          pref.id === id ? { ...pref, [field]: value } : pref
        )
      );
    };
  
    const addPreference = () => {
      setPreferences([...preferences, { id: Date.now(), type: '', value: '' }]);
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
          await createPreference({ preference_type: pref.type, preference_value: pref.value }, token);
        }
        setCurrentPage('home'); // Navigate to home page after setting preferences
      } catch (err) {
        console.error(err.message);
        setError('Failed to submit preferences');
      }
    };
  
    const handleSkip = () => {
      setCurrentPage('home'); // Navigate to home page if the user skips setting preferences
    };
  
    return (
      <div className="form-container-preferences">
        <div className='pref-title'>Set Your Preferences</div>
        <form onSubmit={handlePreferenceSubmit}>
          {preferences.map(pref => (
            <div key={pref.id}>
              <div className="form-group">
                <label htmlFor={`preferenceType-${pref.id}`}>Preference Type</label>
                <div className="preference-dropdown">
                  <div className="dropdown-header" onClick={() => handlePreferenceChange(pref.id, 'type', pref.type ? '' : 'open')}>
                    {pref.type && pref.type !== 'open' ? pref.type : 'Select a preference type'}
                  </div>
                  {pref.type === 'open' && (
                    <div className="dropdown-menu">
                      <div className="dropdown-item" onClick={() => handlePreferenceChange(pref.id, 'type', 'author')}>Author</div>
                      <div className="dropdown-item" onClick={() => handlePreferenceChange(pref.id, 'type', 'genre')}>Genre</div>
                    </div>
                  )}
                </div>
              </div>
              {pref.type && pref.type !== 'open' && (
                <div className="form-group">
                  <label htmlFor={`preferenceValue-${pref.id}`}>Specify {pref.type}</label>
                  <input
                    type="text"
                    id={`preferenceValue-${pref.id}`}
                    name={`preferenceValue-${pref.id}`}
                    placeholder={`Enter ${pref.type}`}
                    required
                    value={pref.value}
                    onChange={(e) => handlePreferenceChange(pref.id, 'value', e.target.value)}
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