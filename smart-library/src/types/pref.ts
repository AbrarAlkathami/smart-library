export type Preference = {
    preference_type: string;
    preference_value: string;
  };

export type UserPreferencesFormProps = {
    setCurrentPage: React.Dispatch<React.SetStateAction<string>>;
  };