import { useForm } from 'react-hook-form';

export interface SearchFormValues {
  query: string;
  format: 'gif' | 'image' | 'video' | 'any';
}

export function SearchFormRHF({ onSubmit }: { onSubmit: (data: SearchFormValues) => void }) {
  const { register, handleSubmit, formState: { errors }, watch } = useForm<SearchFormValues>({
    defaultValues: {
      query: '',
      format: 'gif',
    },
  });

  const queryLength = watch('query')?.length || 0;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <textarea
          {...register('query', {
            required: 'Tell us what you are looking for',
            minLength: { value: 2, message: 'At least 2 characters' },
            maxLength: { value: 2000, message: 'Max 2000 characters' },
          })}
          placeholder="Describe a situation, feeling, or conversation..."
          rows={3}
          style={{
            width: '100%',
            background: 'var(--bg-surface, #141414)',
            border: '1px solid var(--border-default, #2a2a2a)',
            borderRadius: '12px',
            padding: '12px',
            color: 'var(--text-primary, #F5F5F5)',
            fontSize: '1rem',
          }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginTop: '4px', color: '#71717a' }}>
          <span>{queryLength}/2000</span>
          {errors.query && <span style={{ color: '#ef4444' }}>{errors.query.message}</span>}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <select
          {...register('format')}
          style={{
            background: 'var(--bg-surface, #141414)',
            border: '1px solid var(--border-default, #2a2a2a)',
            borderRadius: '8px',
            padding: '8px 12px',
            color: 'var(--text-primary, #F5F5F5)',
          }}
        >
          <option value="gif">GIF</option>
          <option value="image">Image</option>
          <option value="video">Video</option>
          <option value="any">Any</option>
        </select>

        <button
          type="submit"
          style={{
            background: 'var(--brand-purple, #7C3AED)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '8px',
            padding: '8px 18px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Search
        </button>
      </div>
    </form>
  );
}
