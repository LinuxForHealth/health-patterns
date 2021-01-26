/**
 * 
 */
package com.ibm.healthpatterns.app;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.ibm.icu.impl.IllegalIcuArgumentException;

/**
 * A {@link CQLFile}is a reference to a CQL file that is managed by the cohort service.
 * 
 * @author Luis A. Garía
 *
 */
public class CQLFile {

	private static final Pattern CQL_HEADER = Pattern.compile("library\\s+\"?(\\w+)\"?\\s+version\\s+'(.+)\\'");

	private String name;
	private String version;
	
	private String content;

	/**
	 * Create a {@link CQLFile} from the given Path
	 * 
	 * @param file the path
	 * @throws IOException if there are problems reading the given file
	 */
	public CQLFile(Path file) throws IOException {
		this(new String(Files.readAllBytes(file)));
	}
	
	/**
	 * Create a {@link CQLFile} from the given text
	 * 
	 * @param cql the CQL content
	 * @throws IllegalIcuArgumentException if the CQL content is invalid
	 */
	public CQLFile(String cql) throws IllegalIcuArgumentException {
		this.content = cql;
		String lines[] = cql.split("\\r?\\n");
		if (lines.length == 0) {
			throw new IllegalArgumentException("CQL body appears to be all in one line.");
		}
		String firstLine = lines[0];
		Matcher matcher = CQL_HEADER.matcher(firstLine);
		if (matcher.find( )) {
			name = matcher.group(1);
			version = matcher.group(2);
		} else {
			throw new IllegalArgumentException("CQL header is incorrect, expected \"library <name> version '<x.x.x>'\" was: " + cql);
		}
	}

	/**
	 * @return the name
	 */
	public String getId() {
		return toString();
	}

	/**
	 * @return the name
	 */
	public String getName() {
		return name;
	}
	
	/**
	 * @param name the name to set
	 */
	public void setName(String name) {
		this.name = name;
	}
	
	/**
	 * @return the version
	 */
	public String getVersion() {
		return version;
	}
	
	/**
	 * @param version the version to set
	 */
	public void setVersion(String version) {
		this.version = version;
	}
	
	/**
	 * @return the content
	 */
	@JsonIgnore
	public String getContent() {
		return content;
	}

	/**
	 * @param content the content to set
	 */
	public void setContent(String content) {
		this.content = content;
	}
	
	/**
	 * @return the file name for this CQL file 
	 */
	@JsonIgnore
	public String getFileName() {
		return toString() + ".cql";
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
	@Override
	public String toString() {
		return name + "-" + version;
	}
}
