package com.example.upi.entity;

import java.time.Instant;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "idempotency_keys")
public class IdempotencyKey {

	@Id
	@Column(name = "ciphertext_hash", nullable = false, length = 128)
	private String ciphertextHash;

	@Column(nullable = false)
	private Instant processedAt;

	public IdempotencyKey() {
	}

	public String getCiphertextHash() {
		return ciphertextHash;
	}

	public void setCiphertextHash(String ciphertextHash) {
		this.ciphertextHash = ciphertextHash;
	}

	public Instant getProcessedAt() {
		return processedAt;
	}

	public void setProcessedAt(Instant processedAt) {
		this.processedAt = processedAt;
	}
}