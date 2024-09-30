import React from 'react'
import styles from './ToggleSwitch.module.css'

const ToggleSwitch = ({label, onToggle}) => {
    return (
        <div className={styles.container}>
            {label}{' '}
            <div className={styles.toggleswitch}>
                <input
                    type="checkbox"
                    className={styles.checkbox}
                    name={label}
                    id={label}
                    onChange={() => {
                        onToggle()
                    }}
                />
                <label className={styles.label} htmlFor={label}>
                    <span className={styles.inner} />
                    <span className={styles.switch} />
                </label>
            </div>
        </div>
    )
}

export default ToggleSwitch
