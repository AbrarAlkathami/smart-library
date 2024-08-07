import React, { useState } from 'react';
import AddIcon from '../../icons/add-icon.tsx';
import { createPreference } from '../../../services/fetch_preferences.ts'; 
import { Preference, UserPreferencesFormProps } from '../../../types/pref.ts';
import styles from './user_pref_form.module.css';

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
      console.error((err as Error).message);
      setError('Failed to submit preferences');
    }
  };

  const handleSkip = () => {
    setCurrentPage('home'); 
  };

  return (
    <div className={styles.formContainerPreferences}>
      <div className={styles.prefTitle}>Set Your Preferences</div>
      <form onSubmit={handlePreferenceSubmit}>
        {preferences.map((pref, index) => (
          <div key={index}>
            <div className={styles.formGroup}>
              <label htmlFor={`preferenceType-${index}`}>Preference Type</label>
              <div className={styles.preferenceDropdown}>
                <div className={styles.dropdownHeader} onClick={() => handlePreferenceChange(index, 'preference_type', pref.preference_type ? '' : 'open')}>
                  {pref.preference_type && pref.preference_type !== 'open' ? pref.preference_type : 'Select a preference type'}
                </div>
                {pref.preference_type === 'open' && (
                  <div className={styles.dropdownMenu}>
                    <div className={styles.dropdownItem} onClick={() => handlePreferenceChange(index, 'preference_type', 'author')}>Author</div>
                    <div className={styles.dropdownItem} onClick={() => handlePreferenceChange(index, 'preference_type', 'genre')}>Genre</div>
                  </div>
                )}
              </div>
            </div>
            {pref.preference_type && pref.preference_type !== 'open' && (
              <div className={styles.formGroup}>
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
        {error && <div className={styles.error}>{error}</div>}
        <div className={styles.addPreference}>
          <AddIcon onClick={addPreference} />
        </div>
        <div className={styles.prefButtons}>
          <button type="submit">Submit Preferences</button>
          <button type="button" onClick={handleSkip}>Skip</button>
        </div>
      </form>
    </div>
  );
};

export default UserPreferencesForm;
